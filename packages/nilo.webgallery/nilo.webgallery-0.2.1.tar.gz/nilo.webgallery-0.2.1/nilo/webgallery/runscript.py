import BaseHTTPServer
import optparse 

from nilo.webgallery import server

def runner():
    op = optparse.OptionParser()
    op.add_option('-p', type='int', dest='http_port')
    op.add_option('-a', dest='http_address')
    options, args = op.parse_args()
    server_class = BaseHTTPServer.HTTPServer
    handler_class = server.MyRequestHandler
    server_address = (options.http_address or 'localhost', options.http_port or 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    runner()
