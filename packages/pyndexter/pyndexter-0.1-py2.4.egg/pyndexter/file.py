import sys
import codecs
import os
from stat import *
from urlparse import urlsplit, urlunsplit

from pyndexter import Source, Document

class FileSource(Source):
    def __init__(self, root, include=None, exclude=None, predicate=None):
        """ Expose a subset of the file system for searching. """
        Source.__init__(self, include, exclude, predicate)
        self.root = os.path.normpath(root)
        self.encoding = sys.getfilesystemencoding()

    def __iter__(self):
        def walk_path(path):
            path = path.strip(os.path.sep)
            root_path = os.path.join(self.root, path)
            for file in os.listdir(root_path):
                full_path = os.path.join(root_path, file)
                try:
                    stat = os.lstat(full_path)
                except OSError:
                    continue
                if not self.predicate(full_path) or not os.access(full_path, os.R_OK):
                    continue
                if S_ISDIR(stat.st_mode):
                    for file in walk_path(os.path.join(path, file)):
                        yield file
                elif S_ISREG(stat.st_mode):
                    yield (self._file2uri(full_path).decode(self.encoding), stat)

        for file, stat in walk_path('/'):
            self._state[file] = stat.st_mtime
            yield file

    def matches(self, uri):
        scheme, netloc, path, query, fragment = urlsplit(uri, 'file')
        path = os.path.normpath(path)
        return scheme == 'file' and \
               path.startswith(self.root) and \
               self.predicate(path)
            

    def fetch(self, uri):
        path = self._uri2file(uri)
        try:
            stat = os.stat(path)
        except Exception, e:
            raise DocumentNotFound(e)
        return Document(uri, source=self, changed=stat.st_mtime,
                        content=self._fetch_content, size=stat.st_size,
                        created=stat.st_ctime)

    def exists(self, uri):
        return os.path.exists(self._uri2file(uri))

    def _fetch_content(self, uri):
        path = self._uri2file(uri)
        return codecs.open(path, encoding='utf-8', errors='replace').read()

    def __hash__(self):
        return hash(self._file2uri(self.root) + '-'.join(self.exclude) + \
                    '+'.join(self.include))

    # Internal methods
    def _file2uri(self, file):
        return urlunsplit(('file', '', file, '', ''))

    def _uri2file(self, uri):
        scheme, location, path, query, fragment = urlsplit(uri, 'file')
        if scheme not in 'file':
            raise InvalidURI("URI scheme in '%s' not supported by FileSource"
                             % scheme)
        path = os.path.normpath(path)
        if not path.startswith(self.root):
            raise InvalidURI("Requested URI '%s' is not from this FileSource"
                             % uri)
        return path.decode(self.encoding)
