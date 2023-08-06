from tempfile import mkdtemp
from PIL import Image


class Thumbnailer(object):
    def __init__(self):
        self.tempdir = mkdtemp()
        self._last_id = 0
        self._cache = {}

    def tempfile(self):
        self._last_id += 1
        path = '%s/%i.jpg' % (self.tempdir, self._last_id)
        return path, open(path, 'w')

    def get_thumbnail(self, infile):
        """infile: path to file which needs to be converted
           returns path to the thumbnail
        """
        infile = infile[:-7]
        cached_path = self._cache.get(infile)
        if cached_path is not None:
            return cached_path
        outfile_path, outfile = self.tempfile()

        im = Image.open(infile)
        im.thumbnail((128, 128), Image.ANTIALIAS)
        im.save(outfile, "PNG")
        outfile.close()
        self._cache[infile] = outfile_path
        print outfile_path
        return outfile_path
