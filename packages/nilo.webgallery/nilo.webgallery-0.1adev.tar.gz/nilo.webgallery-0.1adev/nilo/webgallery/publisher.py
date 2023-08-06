from nilo.webgallery import template
import StringIO


class Publisher(object):
    def __init__(self):
        pass

    def publish_directory(self, displaypath, contents):
        """displaypath: the path of the directory
           contents: list of tuples with (linkname, linktitle)
           returns stringio with rendered template"""
        results = []
        for linkname, linktitle in contents:
            directory = False
            thumbable = False
            lowered_name = linkname.lower()
            if lowered_name.endswith('.jpg') \
                    or lowered_name.endswith('.png') \
                    or lowered_name.endswith('.gif'):
                itemtype = 'image'
            elif lowered_name.endswith('/'):
                itemtype = 'directory'
            elif lowered_name.endswith('.mov') \
                    or lowered_name.endswith('.3gp') \
                    or lowered_name.endswith('.avi'):
                itemtype = 'movie'
            else:
                continue
            results.append((linkname, linktitle, itemtype))
        results.sort(key=lambda a: a[0].lower())
        f = StringIO.StringIO()
        f.write(template.render(displaypath, results))
        return f

    def publish_file(self, filepath):
        pass
