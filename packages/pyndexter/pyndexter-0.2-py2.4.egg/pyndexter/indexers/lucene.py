# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Lucene
------

The Lucene adapter relies on PyLucene_, which is a Swig interface to a gcj
compiled version of Java Lucene.

PyLucene is good, but there are some serious compatibility issues with Python
threading due to Java threading wanting to be the only implementation running.

Usage
~~~~~

::

    lucene://<path>

Installation
~~~~~~~~~~~~

PyLucene_ is quite difficult to install. Either use your distributions
packaging system or, if you're brave, attempt a source installation. Beyond the
scope of this hint.

.. _PyLucene: http://pylucene.osafoundation.org/

"""

import os
import PyLucene
from pyndexter import *

class LuceneIndexer(Indexer):
    def __init__(self, framework, path):
        Indexer.__init__(self, framework)
        self.path = path
        self.db_path = os.path.join(path, 'lucene.db')
        self.state_path = os.path.join(path, 'store.db')

        create = not os.path.exists(self.db_path) and framework.mode == READWRITE
        self.lucene_store = PyLucene.FSDirectory.getDirectory(self.db_path, create)
        self.analyzer = PyLucene.StandardAnalyzer()

        if framework.mode == READWRITE:
            self.writer = PyLucene.IndexWriter(self.lucene_store, self.analyzer, create)
            self.writer.setMaxFieldLength(1048576) # ??
        else:
            self.writer = None

    def index(self, document):
        doc = PyLucene.Document()
        for k, v in document.attributes.iteritems():
            doc.add(PyLucene.Field(unicode(k), unicode(v),
                                   PyLucene.Field.Store.YES,
                                   PyLucene.Field.Index.TOKENIZED))
        reader = PyLucene.StringReader(document.content)
        doc.add(PyLucene.Field('content', reader))
        self.writer.addDocument(doc)

    def discard(self, uri):
        reader = PyLucene.IndexReader.open(self.db_path)
        reader.deleteDocuments(PyLucene.Term('uri', unicode(uri)))
        reader.close()

    def search(self, query):
        lq = query.as_string()
        searcher = PyLucene.IndexSearcher(self.lucene_store)
        lq = PyLucene.QueryParser('content', self.analyzer).parse(lq)
        #sort_field = PyLucene.SortField('RELEVANCE', False)
        #sort = PyLucene.Sort(sort_field)

        # TODO This is causing a segfault?!?!
        #sort = PyLucene.Sort.INDEXORDER
        #search = searcher.search(query, sort)
        search = searcher.search(lq)
        return LuceneResult(self, query, search)

    def optimise(self):
        self.writer.optimize()

    def flush(self):
        try:
            # XXX Assume this will make it into the Lucene bindings
            self.writer.flush()
        except AttributeError:
            pass

    def close(self):
        if self.writer:
            self.writer.close()


indexer_factory = PluginFactory(LuceneIndexer)


class LuceneResult(Result):
    def __iter__(self):
        for id, hit in self.context:
            yield self._translate(hit)

    def __getitem__(self, index):
        return self._translate(self.context[index])

    def _translate(self, hit):
        attributes = {}
        for field in hit.fields():
            attributes[field.name().encode('utf-8')] = field.stringValue()
        attributes['uri'] = URI(attributes['uri'])
        return Hit(current=self.indexer.framework.fetch,
                   indexed=self.indexer.fetch, **attributes)
