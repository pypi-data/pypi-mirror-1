import os
import itertools

class NotM3uError(Exception):

    def __init__(self, fname):
        self.msg = "File '%s' is not an M3U format file." % fname

class M3uException(Exception):

    def __str__(self):
        return self.msg

class BadM3uEntryFormat(M3uException):

    def __init__(self, line):
        self.msg = "Not a correct M3U line:\n'%s'"

class  MalformattedM3uEntry(M3uException):

    def __init__(self, lineno, line):
        self.msg = "Malformed M3uEntry at line %d: '%s'" % (lineno, line)

class M3uEntryLacksPath(M3uException):

    def __init__(self, lineno):
        self.msg = "M3u entry at line %d lacks media URI" % lineno

class M3uEntry(object):

    def __init__(self, length, title, path, lineno):
        self.length = length
        self.title = title
        self.path = path
        self.infoline = lineno
        self.pathline = lineno + 1
        self._existsfunc = os.path.exists

    @property
    def filename(self):
        # TODO
        raise NotImplementedError

    @property
    def exists(self):
        return self._existsfunc(self.path)

class M3uFileReader(object):

    def __init__(self, fp):
        self.fp = fp
        self.start()

    def start(self):
        self.fp.seek(0)
        self.lc = itertools.count(1)
        first = self.fp.readline().strip()
        if first != '#EXTM3U':
            raise NotM3uError(getattr(self.fp,
                                      'name',
                                      self.fp.__class__.__name__))
        self.lc.next()

    def next(self):
        infoln, pathln = self.lc.next(), self.lc.next()
        infoline, path = (self.fp.readline().strip().split(':'),
                          self.fp.readline().strip())
        if infoline == ['']:
            raise StopIteration
        if path == ['']:
            raise M3uEntryLacksPath(infoln)
        # TODO: Raise on infoline but no path
        if infoline[0] == '#EXTINF':
            # XXX: What about titles with commas?
            length, title = infoline[1].split(',')
            return M3uEntry(length, title, path, infoln)
        else:
            # TODO: Implement line number counting
            raise MalformattedM3uEntry(1, infoline)

class M3u(object):

    def __init__(self, pathOrFile):
        if hasattr(pathOrFile, 'close'):
            self._fp = pathOrFile
        else:
            self.path = pathOrFile

    @property
    def fp(self):
        fp = getattr(self, '_fp', False)
        if fp:
            return fp
        else:
            self._fp = open(self.path, 'r')
            return self._fp

    def __iter__(self):
        self.filereader = M3uFileReader(self.fp)
        return self.filereader

