import BaseHTTPServer
import optparse 
import os
from nilo.webgallery import server

def runner(default_address='localhost', default_port=8080):
    usage = "usage: %prog [options] path"
    description = "Creates a lightweight http server serving an image gallery of the given directory. If no directory is given, it uses the current working directory."
    op = optparse.OptionParser(usage=usage, description=description)
    op.add_option('-p', type='int', dest='http_port')
    op.add_option('-a', dest='http_address')
    options, args = op.parse_args()
    server_class = BaseHTTPServer.HTTPServer
    handler_class = server.MyRequestHandler
    if len(args) == 1 and os.path.isdir(args[0]):
        handler_class.chosen_path = args[0]
    server_address = (options.http_address or default_address,
            options.http_port or default_port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    runner()
