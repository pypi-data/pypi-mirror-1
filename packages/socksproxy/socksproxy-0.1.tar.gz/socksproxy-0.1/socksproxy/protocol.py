import socket
import struct
import select
import logging

class SocksProtocol(object):
    CONNECT = 1
    BIND = 2
    
    VALID_COMMANDS = (BIND, CONNECT)
    VALID_VERSIONS = (4, 5)
    
    GRANTED = chr(90)
    GRANTED5 = chr(0)
    REJECTED_FAILED = chr(91)
    REJECTED_NO_IDENTD = chr(92)
    REJECTED_IDENT_FAILED = chr(93)
    
    def _close(self):
        """
        override to close the connection
        """
        raise NotImplementedError
    
    def _send(self, data):
        """
        override to send data
        """
        raise NotImplementedError

    def _do_proxy(self, peer, to_address):
        """
        override this to call select_proxy or kqueue_proxy or something else
        """
        raise NotImplementedError
            
    def start_connection(self, first_data):
        """
        call this to begin the connection, with the first 1024 bytes
        from the client
        """
        # first, figure out what version the client expects
        self.version = ord(first_data[0])
        self.authenticated = False
        
        try:
            getattr(self, 'handle_version%d' % self.version)(first_data)
        except AttributeError:
            self.reject()
    
        
    def handle_version4(self, data):
        command = ord(data[1])
        to_address = self.resolve_address(data[2:])
        if to_address:
            userid = data[8:data.index('\x00')]
            if command == self.CONNECT:
                self.do_connect_loop(to_address)
            else:
                self.reject()
        else:
            self.reject()
            
    def handle_version5(self, data):
        logging.debug('handling SOCKS5')
        number_of_auths = ord(data[1])
        # for now, let's ignore auth
        response = '\x05\x00'
        self._send(response)
        # we've authenticated, now more data
        self.authenticated = True
    
    def resolve_address(self, data):
        to_host = None
        if self.version == 5:
            addr_type = ord(data[0])
            if addr_type == 3:
                # need to resolve the name
                idx = 2 + ord(data[1])
                name = data[2:idx]
                try:
                    to_host = socket.getaddrinfo(name, None, socket.AF_UNSPEC, socket.SOCK_STREAM)[0][4][0]
                except socket.gaierror:
                    logging.exception("resolving %s", name)
            elif addr_type == 1:
                to_host = socket.inet_ntoa(data[1:5])
                idx = 5
            elif addr_type == 4:
                to_host = socket.inet_ntop(socket.AF_INET6, data[1:17])
                idx = 17
                
        elif self.version == 4:
            # version 4
            to_host = socket.inet_ntoa(data[3:7])
            idx = 1
        if to_host:
            to_port = struct.unpack(">H", data[idx:idx+2])[0]
            return (to_host, to_port)
            
    def handle_version5_request(self, data):
        """
        after authentication, the client should go here
        """
        assert self.authenticated, "Not authenticated!"
        command = ord(data[1])
        to_address = self.resolve_address(data[3:])
        if to_address:
            logging.info('connecting to %s:%s' % to_address)
            if command == self.CONNECT:
                self.do_connect_loop(to_address)
            else:
                self.reject()
        else:
            self.reject()

        
    def reject(self):
        self.respond(self.REJECTED_FAILED)
        self._close()
        
    def respond(self, code, dest_addr=('0.0.0.0', 0)):
        host, port = dest_addr
        if '.' in host:
            family = socket.AF_INET
            addr_family = 1
        else:
            family = socket.AF_INET6
            addr_family = 4
            logging.warn('using ipv6 %s', host)
        ip = socket.inet_pton(family, host)
        port = struct.pack(">H", port)
        if self.version == 4:
            response = '\x00%s%s%s' % (code, port, ip)
        elif self.version == 5:
            response = '\x05%s\x00%s%s%s' % (code, chr(addr_family), ip, port)
        else:
            response = self.REJECTED_FAILED
        self._send(response)
    
    def do_connect_loop(self, to_address):
        peer = self.server.connect_to_peer(to_address, self)
        if peer:            
            self.respond(self.GRANTED5 if self.version == 5 else self.GRANTED, to_address)
            self.server.total_connections += 1
            self._do_proxy(peer, to_address)
        else:
            self.reject()
            
    def select_proxy(self, socket1, socket2, buffsize=4096):
        """
        proxy between sockets using select.select
        """
        sockets = {socket1: socket2, socket2: socket1}

        while sockets:
            r, w, x = select.select(sockets.keys(), [], [])
            for sock in r:
                data = sock.recv(buffsize)
                if data:
                    sockets[sock].sendall(data)
                    continue
                try:
                    sockets[sock].shutdown(socket.SHUT_WR)
                except socket.error:
                    pass
                try:
                    sock.shutdown(socket.SHUT_RD)
                except socket.error:
                    pass
                del sockets[sock]
        socket1.close()
        socket2.close()

    if hasattr(select, 'kqueue'):
        def kqueue_proxy(self, socket1, socket2):
            """
            proxy between sockets using kqueue (available in >=python2.6)
            """
            f1, f2 = socket1.fileno(), socket2.fileno()
            sockets = {f1: socket1, f2: socket2}
            peers = {f1: socket2, f2: socket1}

            kq = select.kqueue()
            kq.control([select.kevent(f1, select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0, 0)
            kq.control([select.kevent(f2, select.KQ_FILTER_READ, select.KQ_EV_ADD)], 0, 0)

            while 1:
                events = kq.control([], 2, None)
                for e in events:
                    fno = e.ident
                    data = sockets[fno].recv(4096)
                    if data:
                        peers[fno].sendall(data)
                    else:
                        socket1.close()
                        socket2.close()
                        kq.close()
                        return
