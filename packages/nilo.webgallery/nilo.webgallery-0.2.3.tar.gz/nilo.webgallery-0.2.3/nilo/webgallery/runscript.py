import BaseHTTPServer
import optparse 

from nilo.webgallery import server

def runner(default_address='localhost', default_port=8080):
    op = optparse.OptionParser()
    op.add_option('-p', type='int', dest='http_port')
    op.add_option('-a', dest='http_address')
    options, args = op.parse_args()
    server_class = BaseHTTPServer.HTTPServer
    handler_class = server.MyRequestHandler
    server_address = (options.http_address or default_address,
            options.http_port or default_port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    runner()
