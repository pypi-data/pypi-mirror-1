# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Used by the Pyndexter unit tests.
"""

from pyndexter import *
from pyndexter.tests.corpus import documents

class MockSource(Source):
    """A mock source class. Uses the documents in pyndexter.tests.corpus."""

    def __iter__(self):
        docs = documents.values()
        docs.sort(key=lambda row: row.uri)
        for doc in docs:
            if self._glob_predicate(doc.uri):
                self._state[unicode(doc.uri)] = doc.changed
                yield doc.uri

    def fetch(self, uri):
        try:
            return documents[unicode(uri)]
        except KeyError:
            raise DocumentNotFound(uri)

    def matches(self, uri):
        return uri.scheme == 'mock'

    def exists(self, uri):
        return unicode(uri) in documents

    def __hash__(self):
        uris = documents.keys()
        uris.sort()
        return hash(','.join((uris)))


source_factory = PluginFactory(MockSource,
                               include=PluginFactory.List(str),
                               exclude=PluginFactory.List(str))
