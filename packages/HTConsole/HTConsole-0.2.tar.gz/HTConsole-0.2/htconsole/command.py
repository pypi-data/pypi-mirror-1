import sys
import optparse
import pkg_resources
from paste import httpserver
import socket

my_package = pkg_resources.get_distribution('HTConsole')

help = """\
Starts up a local web server that you can use as a Python interactive
console of sorts.
"""

parser = optparse.OptionParser(
    version=str(my_package),
    usage="%%prog [OPTIONS]\n\n%s" % help)
parser.add_option('--files',
                  metavar="DIR",
                  dest="save_dir",
                  default="./python/",
                  help="Directory to save and load files from")
parser.add_option('--doctests',
                  metavar="DIR",
                  dest="doctest_dir",
                  default="./doctests/",
                  help="Directory to find doctests in (doctests/ by default)")
parser.add_option('--port',
                  metavar="PORT",
                  dest="port",
                  type="int",
                  help="Specify a port to connect to (by default the first free port after 8000 will be used)")
parser.add_option('--no-browser',
                  action="store_false",
                  default=True,
                  dest="open_browser",
                  help="Don't open up a browser after starting the server (the address will be printed either way)")
parser.add_option('--log-http',
                  action="store_true",
                  dest="log_http",
                  help="Show (on the console) a log of transactions as they pass by")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    if args:
        parser.error('No arguments accepted! (%s)' % args)
    if options.port is None:
        options.port = find_port('127.0.0.1', 8000)
    from htconsole.wsgiapp import make_app
    app = make_app({'debug': True},
                   doctest_dir=options.doctest_dir,
                   save_dir=options.save_dir)
    if options.log_http:
        from paste.translogger import TransLogger
        app = TransLogger(app)
    server = httpserver.serve(app, host='127.0.0.1',
                              port=options.port,
                              start_loop=False)
    location = 'http://localhost:%s' % options.port
    print 'Serving from: %s' % location
    if options.open_browser:
        import webbrowser
        webbrowser.open(location, True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def find_port(host, port):
    while 1:
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error:
            port += 1
        else:
            s.close()
            return port
        
if __name__ == '__main__':
    main()
    
