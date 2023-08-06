import SocketServer
import socket
import time
import logging

import protocol
import ssh


class SocksHandler(SocketServer.StreamRequestHandler, protocol.SocksProtocol):
    
    def handle(self):
        data = self.request.recv(64)
        if data:
            self.start_connection(data)
            if self.version == 5 and self.authenticated:
                self.handle_version5_request(self.request.recv(256))
        else:
            self.request.close()
            
    def _close(self):
        self.request.close()
    
    def _send(self, data):
        self.wfile.write(data)
        
    
    def _do_proxy(self, peer, to_address):
        if hasattr(self, 'kqueue_proxy'):
            self.kqueue_proxy(self.request, peer)
        else:
            self.select_proxy(self.request, peer)
        logging.info('disconnected from %s:%s' % to_address)

    
class SocksServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    total_connections = 0
    max_simultaneous_connections = 100
    current_connections = 0
    
    def __init__(self, listen_addr):
        SocketServer.ThreadingTCPServer.__init__(self, listen_addr, SocksHandler)
    
    def start(self):
        self.serve_forever()
    
    # def close_request(self, request):
    #     SocketServer.ThreadingTCPServer.close_request(self, request)
    #     self.current_connections -= 1
    # 
    # def process_request(self, request, client_address):
    #     i = 0
    #     while self.current_connections > self.max_simultaneous_connections:
    #         # logging.warning('too many connections %d', self.current_connections)
    #         time.sleep(0.5)
    #         i += 1
    #         if i == 60:
    #             request.close()
    #             return
    #     self.current_connections += 1
    #     SocketServer.ThreadingTCPServer.process_request(self, request, client_address)
        
    def connect_to_peer(self, to_address, handler):
        try:
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            peer.connect(to_address)
            return peer
        except socket.error:
            logging.exception('connecting to %s:%s' % to_address)


class SSHSocksServer(SocksServer):
    def __init__(self, listen_addr, ssh_client):
        SocksServer.__init__(self, listen_addr)
        self.client = ssh_client
        self.transport = ssh_client.get_transport()
        
    def connect_to_peer(self, to_addr, handler):
        try:
            chan = self.transport.open_channel('direct-tcpip',
                                               to_addr,
                                               handler.client_address)
            return chan
        except Exception:
            logging.exception("connecting to %s:%s" % to_addr)

        
    