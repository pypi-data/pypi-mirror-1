from optparse import OptionParser
import logging


def main():

    parser = OptionParser()
    parser.add_option('-p', dest='port', default=1080, type='int',
                      help='SOCKS port')
    parser.add_option('-s', dest='ssh_host', default='', help='SSH host')
    parser.add_option('-P', dest='ssh_port', default=22, help='SSH port', type='int')
    parser.add_option('-u', dest='ssh_user', default=None, help='SSH user')
    parser.add_option('-k', dest='ssh_key', default='', help='SSH key')
    parser.add_option('-d', dest='debug', default=False, help='debug mode', action='store_true')
    parser.add_option('-t', dest='server_type', default='threaded', help='which server (async, threaded)')

    options, args = parser.parse_args()
    host = '127.0.0.1'
    
    logging.basicConfig(level=logging.DEBUG if options.debug else logging.INFO)
    
    if options.server_type == 'threaded':
        import blocking_socks as module
    else:
        import async_socks as module
    print module
    
    if options.ssh_host:
        import ssh
        
        client = ssh.get_client(options.ssh_host,
                    keyfile=options.ssh_key,
                    username=options.ssh_user,
                    port=options.ssh_port)
        server = module.SSHSocksServer((host, options.port), client)
    else:
        server = module.SocksServer((host, options.port))
    
    logging.info('%s serving on %s:%s', server, host, options.port)
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    logging.debug('handled %d connections', server.total_connections)
    

if __name__ == '__main__':
    import sys
    sys.exit(main())
