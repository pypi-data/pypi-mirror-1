import asyncore
import asynchat
import socket
import traceback
import time
import logging

import protocol

    
class SocksServer(asyncore.dispatcher):    
    def __init__(self, listen_addr):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(listen_addr)
        self.listen(5)
        self.total_connections = 0
        
    def handle_accept(self):
        SocksHandler(self, self.accept())
        
    def connect_to_peer(self, to_addr, handler):
        return PeerConnection(handler, to_addr)
        
    def start(self):
        try:
            asyncore.loop(use_poll=True)
        except KeyboardInterrupt:
            asyncore.close_all()
            return

        
class SSHSocksServer(SocksServer):
    """
    A SOCKS4/5 proxy that tunnels traffic over 
    an SSH connection
    """
    def __init__(self, listen_addr, ssh_client):
        
        self.client = ssh_client
        self.transport = ssh_client.get_transport()
        
        SocksServer.__init__(self, listen_addr)
    
    def connect_to_peer(self, to_addr, handler):
        try:
            chan = self.transport.open_channel('direct-tcpip',
                                               to_addr,
                                               handler.addr)
            return PeerConnection(handler, to_addr, chan)
        except Exception:
            logging.exception("connecting to %s:%s" % to_addr)


class SocksHandler(asyncore.dispatcher_with_send, protocol.SocksProtocol):
    
    def __init__(self, server, (conn, addr)):
        asyncore.dispatcher_with_send.__init__(self, conn)
        self.server = server
        self.bufsize = 256
        self._connected = False
        self.peer = None
        
    def _close(self):
        self.close()

    def _send(self, data):
        asyncore.dispatcher_with_send.send(self, data)

    def _do_proxy(self, peer, to_address):
        self.peer = peer
        self.bufsize = 4096
    
    # def readable(self):
    #     if self.peer and not self.peer.connected:
    #         return False
    #     else:
    #         return True
            
    def handle_read(self):
        data = self.recv(self.bufsize)
        if not data:
            return
        if self.peer:
            # logging.debug(repr(data))
            
            try:
                self.peer.push(data)
            except socket.error, e:
                if e.args[0] == 9:
                    self.peer.close()
                    self.close()
        else:
            if not self._connected:
                self.start_connection(data)
                self._connected = True
            else:
                if self.version == 5 and self.authenticated:
                    self.handle_version5_request(data)
    
    def handle_close(self):
        self.close()
        if self.peer:
            self.peer.close()
        

class PeerConnection(asynchat.async_chat):
    def __init__(self, client, to_addr, to_socket=None):
        if to_socket is not None:
            asynchat.async_chat.__init__(self, to_socket)
        else:
            asynchat.async_chat.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(to_addr)
        self.client = client
        self.to_addr = to_addr
        self.set_terminator(None)
        
    def handle_connect(self):
        pass
        
    def collect_incoming_data(self, data):
        self.client.send(data)
    
    def handle_close(self):
        self.client.close()
        self.close()
        logging.info('disconnected from %s:%s' % self.to_addr)
