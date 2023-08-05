import os
from pyndexter import *
import xapwrap.index as xi
import xapwrap.document as xd


# XXX Is a numeric ID the only way to uniquely identify documents in Xapian?
# XXX This seems crazy, and prone to error.
def uri2id(uri):
    return abs(hash(uri))


xd.Document.registerFlattener(long, xd.flattenNumeric)
xd.Document.registerFlattener(float, xd.flattenNumeric)


class XapianIndexer(Indexer):
    capabilities = CAP_ORDERING | CAP_READONLY | CAP_ATTRIBUTES | \
                   CAP_RELEVANCE | CAP_HITCOUNT | CAP_LIST | CAP_WHOLEWORD | \
                   CAP_INTERSECTION

    def __init__(self, path, source=None, mode=READWRITE):
        Indexer.__init__(self, source, mode, os.path.join(path, 'state.db'))
        self.path = path
        self._init_env(self.path)
        self.idx_path = os.path.join(path, 'xapian.db')
        if mode == READWRITE:
            self.idx = xi.SmartIndex(self.idx_path, True)
        else:
            self.idx = xi.SmartReadOnlyIndex(self.idx_path)

    def index(self, document):
        self._assert_rw()
        if isinstance(document, basestring):
            document = self.fetch(document)

        sort_fields = [xd.SortKey(u'uri', document.uri)]
        sort_fields += [xd.SortKey(k, v) for k, v in 
                        document.attributes.iteritems()
                        if v is not None and k != 'uri']
        doc = xd.Document(
                textFields=xd.TextField(document.content),
                sortFields=sort_fields,
                uid=uri2id(document.uri),
                source=document.uri)

        self.idx.index(doc)

    def discard(self, document):
        self._assert_rw()
        if isinstance(document, Document):
            document = document.uri
        self.idx.delete_document(uri2id(document))

    def sync(self):
        if self.mode == READWRITE:
            self._assert_rw()
            self.idx.flush()
            self._sync_source_state()

    def close(self):
        self.sync()
        self.idx.close()
        self.idx = None

    def search(self, phrase, flags=0, order_by=None, order_ascending=True,
               order_type=str):
        phrase = phrase.encode('utf-8')
        if order_by == 'relevance':
            order_args = {'sortByRelevence': True}
        else:
            order_args = {'sortKey': order_by}
        search = self.idx.search(phrase, sortAscending=order_ascending,
                                 **order_args)
        return XapianSearch(self, phrase, search)


class XapianSearch(Search):
    def __iter__(self):
        for hit in self.context:
            doc = self.indexer.idx.get_document(hit['uid'])
            # XXX Is this the actual way to get values out?!?!?
            yield Hit(doc.get_value(self.indexer.idx.indexValueMap['uri']),
                      document=self.indexer.fetch)

    def __len__(self):
        return len(self.context)

    def __getitem__(self, index):
        doc = self.indexer.idx.get_document(self.context[index]['uid'])
        return Hit(doc.get_value(self.indexer.idx.indexValueMap['uri']),
                   document=self.indexer.fetch)
