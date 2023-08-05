import os
import hype
from pyndexter import *

class HyperestraierIndexer(Indexer):
    capabilities = CAP_READONLY | CAP_CONTENT | CAP_ATTRIBUTES | CAP_ORDERING |\
                   CAP_HITCOUNT | CAP_LIST | CAP_RELEVANCE | CAP_WHOLEWORD | \
                   CAP_ASTERISK | CAP_INTERSECTION

    def __init__(self, path, source=None, mode=READWRITE, hype_mode=None):
        Indexer.__init__(self, source, mode, os.path.join(path, 'state.db'))
        self.path = path
        self._init_env(self.path)
        self.hype_path = os.path.join(self.path, 'hyperestraier.db')
        if hype_mode is None:
            hype_mode = 0
            if mode == READONLY:
                hype_mode |= hype.ESTDBREADER
            elif mode == READWRITE:
                hype_mode |= hype.ESTDBWRITER|hype.ESTDBCREAT
        self.db = hype.Database(self.hype_path, hype_mode)

    def fetch(self, uri):
        if self.source:
            return self.source.fetch(uri)
        doc = self.db.get_doc_by_uri(uri)
        if doc is None:
            raise DocumentNotFound(uri)
        attributes = self._translate_attributes(doc)
        return Document(content=doc.text, source=self.source, **attributes)

    def index(self, document):
        self._assert_rw()
        if isinstance(document, basestring):
            document = self.fetch(document)
        hdoc = hype.Document()
        for k, v in document.attributes.iteritems():
            hdoc['@' + k] = v
        hdoc.add_text(document.content)
        self.db.put_doc(hdoc)

    def discard(self, document):
        self._assert_rw()
        if isinstance(document, Document):
            document = document.uri
        doc = self.db.get_doc_by_uri(document)
        if not doc:
            raise DocumentNotFound(document)
        self.db.remove(doc)

    def search(self, phrase, flags=0, order_by=None,
               order_ascending=True, order_type=str):
        phrase = ((not flags & SEARCH_UNION) and ' ' or '|').join(phrase.split())
        order = None
        if order_by is not None:
            if order_type is int:
                order_type = 'NUM'
            else:
                order_type = 'STR'
            order = u'@%s %s%s' % (order_by, order_type,
                                   order_ascending and 'A' or 'D')
        if not flags & SEARCH_ASTERISK:
            phrase = phrase.replace('*', '\\*')
        if not flags & SEARCH_QUESTION:
            phrase = phrase.replace('?', '\\?')
        if not flags & SEARCH_WHOLEWORD:
            phrase = '*' + '* *'.join(phrase.split()) + '*'
        return self.hype_search(phrase, order=order)

    def hype_search(self, phrase, simple=True, order=None):
        """ Full Hyperestraier search phrase. """
        search = self.db.search(phrase, simple=simple)
        if order is not None:
            search = search.order(order)
        return HyperestraierSearch(self, phrase, search)

    def optimize(self):
        self._assert_rw()
        self.db.optimize()

    def sync(self):
        if self.mode == READWRITE:
            self.db.sync()
            self._sync_source_state()

    def close(self):
        if self.mode == READWRITE:
            self.sync()
        self.db = None

    # Internal methods
    def _translate_attributes(self, hdoc):
        attributes = {}
        for k in hdoc.attributes:
            if k[0] == '@':
                attributes[k[1:]] = hdoc.get(k)
            else:
                attributes[k] = hdoc.get(k)
        return attributes


class HyperestraierSearch(Search):
    def __iter__(self):
        for doc in self.context:
            # How do we get the score?
            yield Hit(document=self.indexer.fetch,
                      **self.indexer._translate_attributes(doc))

    def __len__(self):
        return len(self.context)

    def __getitem__(self, index):
        return self.context[index]['@uri']
