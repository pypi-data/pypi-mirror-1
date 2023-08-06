import os.path
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('nilo.webgallery', 'templates'))

BASEPATH = os.path.dirname(__file__)

def _getpath(filename):
    return os.path.join(BASEPATH, 'resources', filename)
JQUERY = open(_getpath('jquery-latest.pack.js')).read()
THICKBOX = open(_getpath('thickbox-compressed.js')).read()
STYLES = open(_getpath('style.css')).read()

class PageInfo(object):
    def __init__(self, path, contents):
        self.path = path
        self.contents = contents
        path_elems = path[1:].split('/')
        pathbar = ['<a href="/">Home</a>' ]
        c = 0
        path_len = len(path_elems)
        for elem in path_elems:
            c += 1
            if c < path_len:
                fullpath = '/'.join(path_elems[0:c])
                pathbar.append('<a href="/%s/">%s</a>' % (fullpath, elem))
        self.pathbar = '%s %s' % (' / '.join(pathbar), elem)

def render(path, contents):
    pageinfo = PageInfo(path, contents)
    template = env.get_template('default.html')
    return template.render(context=pageinfo, thickbox=THICKBOX, styles=STYLES, jquery=JQUERY)
