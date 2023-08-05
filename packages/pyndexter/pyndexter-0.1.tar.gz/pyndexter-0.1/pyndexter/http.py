import heapq
import formatter
import htmllib
import urllib2
import time
from StringIO import StringIO
from urlparse import urlsplit, urlunsplit, urljoin, urldefrag
from pyndexter import *
from pyndexter.util import CacheDict
try:
    set = set
except:
    from sets import Set as set


class Parser(htmllib.HTMLParser):
    def __init__(self, encoding):
        htmllib.HTMLParser.__init__(self, formatter.NullFormatter())
        self.content = StringIO()
        self.hrefs = []
        self.encoding = encoding

    def handle_data(self, data):
        self.content.write(data.decode(self.encoding, 'replace'))

    def anchor_bgn(self, href, name, type):
        self.hrefs.append(href.decode(self.encoding, 'replace'))


class HTTPSource(Source):
    """ A web crawling document source. """
    def __init__(self, seed, include=None, exclude=None, predicate=None, cache=32):
        if not include:
            include = [seed + '*']
        Source.__init__(self, include, exclude, predicate)
        self.seed = seed
        self._cache = CacheDict(cache)

    def __iter__(self):
        traversed = set()
        def walk_uri(uri):
            uri = urldefrag(uri)[0]
            if uri in traversed:
                return
            traversed.add(uri)
            try:
                doc, hrefs = self._fetch(uri)
            except DocumentNotFound:
                return
            self._state[uri] = doc.changed
            yield doc.uri
            for href in [href for href in  hrefs if self.predicate(href)]:
                for child_uri in walk_uri(href):
                    yield child_uri

        for uri in walk_uri(self.seed):
            yield uri

    def matches(self, uri):
        scheme, netloc, path, query, fragment = urlsplit(uri)
        return scheme in ('http', 'https') and self.predicate(uri)

    def fetch(self, uri):
        self._validate_uri(uri)
        return self._fetch(uri)[0]

    def __hash__(self):
        return hash(self.seed + '-'.join(self.exclude) + '+'.join(self.include))

    # Internal methods
    def _validate_uri(self, uri):
        if not self.matches(uri):
            raise InvalidURI("URI '%s' is not supported by this HTTPSource" % uri)

    def _fetch(self, uri):
        uri = urldefrag(uri)[0]
        if uri in self._cache:
            return self._cache[uri]
        try:
            handle = urllib2.urlopen(uri)
            info = handle.info()
            content_type = info.get('Content-Type', 'text/html;charset=utf-8')
            content_encoding = 'utf-8'
            if ';' in content_type:
                content_type, parms = content_type.split(';', 1)
                for k, v in [parm.split('=', 1) for parm in parms.split(';')]:
                    if k == 'charset':
                        content_encoding = v
            if 'Last-Modified' in info:
                changed = time.mktime(time.strptime(info['Last-Modified'],
                                      '%a, %d %b %Y %H:%M:%S GMT'))
            else:
                changed = 0
            content = handle.read()
            if content_type.startswith('text/html'):
                parser = Parser(content_encoding)
                parser.feed(content)
                content = parser.content.getvalue()
                hrefs = set([urljoin(uri, h, False).decode('utf-8') for h in parser.hrefs])
            else:
                content = handle.read().decode('utf-8', 'replace')
                hrefs = []
            doc = Document(uri, content=content,
                           changed=changed, content_type=content_type.decode('utf-8'),
                           content_encoding=content_encoding.decode('utf-8'))
            self._cache[uri] = (doc, hrefs)
            return (doc, hrefs)
        except urllib2.URLError, e:
            raise DocumentNotFound("Could not fetch URI '%s'. Exception was "
                                   "%s: %s" % (uri, e.__class__.__name__, str(e)))
