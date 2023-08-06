import socks
import time
import httplib2
import sys

p = httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_SOCKS5, proxy_host='localhost', proxy_port=int(sys.argv[1]))
# s = socks.socksocket()

# s.setproxy(socks.PROXY_TYPE_SOCKS4, '127.0.0.1', 1080, False)

# s.connect(('google.com', 80))
# s.sendall('GET / HTTP/1.0\r\n\r\n')
# print s.recv(8192)
# time.sleep(5)
# s.close()


h = httplib2.Http(proxy_info=p)

for i in range(3):
    print len(h.request('http://google.com/', 'GET')[1])

print len(h.request('http://tabblo.com/studio/', 'GET')[1])