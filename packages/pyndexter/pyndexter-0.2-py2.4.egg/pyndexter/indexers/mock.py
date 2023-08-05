# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Memory-only indexer used primarily for unit testing. Takes no options.
"""

from StringIO import StringIO
from pyndexter import *


class MockStateStore(StateStore):
    """Memory-only StateStore."""
    def __init__(self):
        self.stored = False
        self.buffer = StringIO()

    def store(self):
        self.stored = True
        self.buffer = StringIO()
        return self.buffer

    def retrieve(self):
        self.buffer.seek(0)
        return self.buffer

    def exists(self):
        return self.stored


class MockIndexer(Indexer):
    """Memory-only indexer."""

    def __init__(self, framework, path=None):
        Indexer.__init__(self, framework)
        self.close()

    def close(self):
        self.attributes = {}
        self.cache = {}

    def __iter__(self):
        uris = self.attributes.keys()
        uris.sort()
        for uri in uris:
            yield uri

    def fetch(self, uri):
        try:
            return Document(content=self.cache[uri], quality=0.99,
                            **self.attributes[uri])
        except KeyError:
            raise DocumentNotFound(uri)

    def discard(self, uri):
        del self.attributes[uri]
        del self.cache[uri]

    def index(self, document):
        from copy import copy
        self.attributes[document.uri] = copy(document.attributes)
        self.cache[document.uri] = document.content

    def state_store(self):
        return MockStateStore()

    def search(self, query):
        docs = self.cache.keys()
        docs.sort()
        return MockResult(self, query, docs)


indexer_factory = PluginFactory(MockIndexer)


class MockResult(Result):
    def __iter__(self):
        for uri in self.context:
            if self.query(self.indexer.framework.reduce(self.indexer.cache[uri].lower())):
                yield self._translate(uri)

    def __getitem__(self, index):
        return self._translate(self.context[index])

    def _translate(self, uri):
        attributes = self.indexer.attributes[uri]
        return Hit(current=self.indexer.framework.fetch,
                   indexed=self.indexer.fetch, **attributes)
