import getpass
import socket
from paramiko.client import SSHClient, WarningPolicy
from paramiko.resource import ResourceManager
from paramiko.transport import Transport
from paramiko.ssh_exception import SSHException, ChannelException, BadHostKeyException


# override sshclient because it doesn't have a hook for enabling compression
class CompressibleSSHClient(SSHClient):
    def connect(self, hostname, port=22, username=None, password=None, pkey=None,
                key_filename=None, timeout=None, allow_agent=True, look_for_keys=True):
        addrs = [(family, sockaddr) for (family, socktype, proto, canonname, sockaddr) in socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM) if socktype == socket.SOCK_STREAM]
        if not addrs:
            raise SSHException('No suitable address family for %s' % hostname)
        for af, addr in addrs:
            sock = socket.socket(af, socket.SOCK_STREAM)
            if timeout is not None:
                try:
                    sock.settimeout(timeout)
                except:
                    pass
            try:
                sock.connect(addr)
            except socket.error:
                continue
            else:
                break
        else:
            raise SSHException("No suitable addresses: %s" % addrs)
        t = self._transport = Transport(sock)
        
        #####
        #####  here's the overridden part
        #####
        t.use_compression(True)
        
        if self._log_channel is not None:
            t.set_log_channel(self._log_channel)
        t.start_client()
        ResourceManager.register(self, t)

        server_key = t.get_remote_server_key()
        keytype = server_key.get_name()

        if port == 22:
            server_hostkey_name = hostname
        else:
            server_hostkey_name = "[%s]:%d" % (hostname, port)
        our_server_key = self._system_host_keys.get(server_hostkey_name, {}).get(keytype, None)
        if our_server_key is None:
            our_server_key = self._host_keys.get(server_hostkey_name, {}).get(keytype, None)
        if our_server_key is None:
            # will raise exception if the key is rejected; let that fall out
            self._policy.missing_host_key(self, server_hostkey_name, server_key)
            # if the callback returns, assume the key is ok
            our_server_key = server_key

        if server_key != our_server_key:
            raise BadHostKeyException(hostname, server_key, our_server_key)

        if username is None:
            username = getpass.getuser()

        if key_filename is None:
            key_filenames = []
        elif isinstance(key_filename, (str, unicode)):
            key_filenames = [ key_filename ]
        else:
            key_filenames = key_filename
        self._auth(username, password, pkey, key_filenames, allow_agent, look_for_keys)


def get_client(host, keyfile=None, username=None, port=22):
    client = CompressibleSSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(WarningPolicy())
    client.connect(host,
                   port, 
                   username=username,
                   key_filename=keyfile,
                   look_for_keys=True)
    
    return client
    