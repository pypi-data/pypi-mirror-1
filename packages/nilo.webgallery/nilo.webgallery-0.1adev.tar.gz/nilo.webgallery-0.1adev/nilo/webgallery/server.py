from nilo.webgallery import publisher, thumbnailer
import SimpleHTTPServer
import BaseHTTPServer
import cgi
import os
import urllib
import cgi


thumbnailer_tool = thumbnailer.Thumbnailer()
publisher_tool = publisher.Publisher()

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        if path.endswith('++thumb'):
            path = thumbnailer_tool.get_thumbnail(path)

        ctype = self.guess_type(path)
        if self.path in ('/res/macFFBgHack.png', '/res/loadingAnimation.gif'):
            path = os.path.join(os.path.dirname(__file__), 'resources', path.split('/')[-1])
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(os.fstat(f.fileno())[6]))
        self.end_headers()
        return f



    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        displaypath = cgi.escape(urllib.unquote(self.path))
        contents = []
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            linkname = urllib.quote(linkname)
            displayname = cgi.escape(displayname)
            contents.append((linkname, displayname))
        to_publish = publisher_tool.publish_directory(displaypath, contents)
        length = to_publish.tell()
        to_publish.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return to_publish

server_class=BaseHTTPServer.HTTPServer
handler_class=MyRequestHandler 
server_address = ('', 8000)
httpd = server_class(server_address, handler_class)
httpd.serve_forever()

