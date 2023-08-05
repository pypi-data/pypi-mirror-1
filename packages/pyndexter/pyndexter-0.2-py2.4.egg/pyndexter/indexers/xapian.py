# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Xapian
------

Adapter for `Xapian <http://www.xapian.org>`_, a fast full-text indexing
engine.

Usage
~~~~~

::

    xapian://<path>

Installation
~~~~~~~~~~~~

Install Xapian for your distribution (typically the package ``xapian-core``).

If your distribution also includes the SWIG bindings, install these, otherwise:

::

    wget http://www.oligarchy.co.uk/xapian/0.9.9/xapian-bindings-0.9.9.tar.gz
    tar xfzv xapian-bindings-0.9.9.tar.gz
    cd xapian-bindings-0.9.9
    ./configure
    make
    make install
"""

import os
import re
from pyndexter import *
xapian = __import__('xapian')


__all__ = ['XapianIndexer', 'XapianResult']


class XapianIndexer(Indexer):
    def __init__(self, framework, path):
        Indexer.__init__(self, framework)

        framework.reduce.split = True

        path = path.encode('utf-8')
        self.path = path
        self.xapian_path = os.path.join(path, 'xapian.db')
        self.state_path = os.path.join(path, 'state.db')

        if self.framework.mode == READWRITE:
            if not os.path.exists(self.xapian_path):
                os.makedirs(self.xapian_path)
            self.db = xapian.flint_open(self.xapian_path,
                                        xapian.DB_CREATE_OR_OPEN)
        else:
            self.db = xapian.flint_open(self.xapian_path)

    def index(self, document):
        doc = xapian.Document()

        # FIXME Xapian doesn't support UTF-8 yet. "Coming soon."
        content = document.content.encode('utf-8')
        uri = unicode(document.uri).encode('utf-8')

        doc.set_data(content)

        doc.add_term('Q' + uri)

        words = self.framework.reduce(content)
        for word in words:
            doc.add_posting(word, 0)

        self.db.replace_document('Q' + uri, doc)

    replace = index

    def discard(self, uri):
        self.db.delete_document('Q' + unicode(uri).encode('utf-8'))

    def fetch(self, uri):
        term = 'Q' + unicode(uri).encode('utf-8')
        for docid in self.db.postlist(term):
            doc = self.db.get_document(docid[0])
            # TODO fetch attributes
            return Document(uri=uri, content=doc.get_data().decode('utf-8'),
                            quality=0.95)
        raise DocumentNotFound(uri)

    def __iter__(self):
        terms = self.db.allterms()
        terms.skip_to('Q')
        for term in terms:
            if term[0][0] != 'Q':
                return
            yield term[0][1:].decode('utf-8')

    def flush(self):
        self.db.flush()

    def close(self):
        self.flush()
        #self.db.close()
        self.db = None

    def search(self, query):

        # Fake stemmer to use the frameworks
        framework = self.framework
        query.reduce(self.framework.reduce)
        query_parser = xapian.QueryParser()
        xq = query_parser.parse_query(query.as_string().encode('utf-8').lower())
        enquire = xapian.Enquire(self.db)
        enquire.set_query(xq)
        return XapianResult(self, query, enquire)


indexer_factory = PluginFactory(XapianIndexer, max_word_length=int)


class XapianResult(Result):
    def __iter__(self):
        matches = self.context.get_mset(0, 20)
        for hit in matches:
            yield self._translate(hit)

    def __getitem__(self, index):
        matches = self.context.get_mset(index, 1)
        for hit in matches:
            return self._translate(hit)
        return matches.next()

    def __getslice__(self, i, j):
        for hit in self.context.get_mset(i, j - i):
            yield self._translate(hit)

    def __len__(self):
        return len(self.context)

    # Internal methods
    def _translate(self, hit):
        doc = hit[xapian.MSET_DOCUMENT]
        terms = doc.termlist()
        terms.skip_to('Q')
        uri = terms.next()[0][1:]
        assert uri, 'uniQue term (URI) not found in document term list'
        return Hit(URI(uri),
                   current=self.indexer.framework.fetch,
                   indexed=self.indexer.fetch,
                   did=hit[xapian.MSET_DID],
                   score=float(hit[xapian.MSET_PERCENT]) / 100.0)

