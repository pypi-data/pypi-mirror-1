# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Hype
----

Adapter for Hyperestraier using the Hype bindings.

Hype_ is a Python wrapper for Hyperestraier_. Hype is only available through
SVN, but is quite stable and functional.

.. _Hype: http://hype.python-hosting.com
.. _Hyperestraier: http://hyperestraier.sourceforge.net/

Usage
~~~~~

::

    hype://<path>?hype_mode=<int>&enable_scoring=<bool>


``hype_mode`` (default: auto)
    Override the default ``READONLY``/``READWRITE`` modes in Pyndexter and use
    Hyperestraier database open modes. See the Hyperestraier docs for details.

``enable_scoring`` (default: ``true``)
    Put Hyperestraier into a debug mode where scores are returned. This is
    apparently somewhat slower, but I have not observed a massive difference.

Installation
~~~~~~~~~~~~

Install your distributions Hyperestraier package.

::

    svn co http://svn.hype.python-hosting.com/trunk hype
    cd hype
    python setup.py install
"""

import os
from pyndexter import *
hype = __import__('hype')


__all__ = ['HypeIndexer', 'HypeResult']


class HypeIndexer(Indexer):
    def __init__(self, framework, path, hype_mode=0, enable_scoring=True):
        Indexer.__init__(self, framework)
        self.path = path
        self.hype_path = os.path.join(self.path, 'hype.db')
        self.state_path = os.path.join(self.path, 'state.db')
        self.enable_scoring = enable_scoring

        if framework.mode == READONLY:
            hype_mode |= hype.ESTDBREADER
        elif framework.mode == READWRITE:
            hype_mode |= hype.ESTDBWRITER
            if not os.path.exists(self.hype_path):
                hype_mode |= hype.ESTDBCREAT
                os.makedirs(self.path)

        self.db = hype.Database(self.hype_path, hype_mode)

    def index(self, document):
        hdoc = hype.Document(unicode(document.uri))
        for k, v in document.attributes.iteritems():
            if k != 'uri':
                hdoc['@' + k] = unicode(v)
        for line in document.content.splitlines():
            hdoc.add_text(line)
        self.db.put_doc(hdoc)

    def discard(self, uri):
        doc = self.db.get_doc_by_uri(unicode(uri))
        if not doc:
            raise DocumentNotFound(uri)
        self.db.remove(doc)

    def search(self, query):
        qs = query.as_string(not_='ANDNOT ').decode('utf-8')
        search = self.db.search(qs)
        return HypeResult(self, query, search, self.enable_scoring)

    def optimise(self):
        self.db.optimize()

    def fetch(self, uri):
        doc = self.db.get_doc_by_uri(unicode(uri))
        if not doc:
            raise DocumentNotFound(uri)
        attributes = self._translate_attributes(doc)
        return Document(content='\n'.join(doc.texts), quality=0.99, **attributes)

    def flush(self):
        self.db.sync()
        self.db.flush()

    def close(self):
        self.db = None

    # Internal methods
    def _translate_attributes(self, hdoc):
        attributes = {}
        for k in hdoc.attributes:
            if k[0] == '@':
                attributes[k[1:]] = hdoc.get(k)
            else:
                attributes[k] = hdoc.get(k)
        attributes['uri'] = URI(attributes['uri'])
        return attributes


indexer_factory = PluginFactory(HypeIndexer, hype_mode=int,
                                   enable_scoring=bool)


class HypeResult(Result):
    def __init__(self, indexer, query, context, enable_scoring=True):
        self.enable_scoring = enable_scoring
        if enable_scoring:
            context = context.scores().option(hype.ESTCONDSCFB)
        Result.__init__(self, indexer, query, context)

    def __iter__(self):
        if self.enable_scoring:
            for doc, score in self.context:
                yield self._translate(doc, score)
        else:
            for doc in self.context:
                yield self._translate(doc)

    def __len__(self):
        return len(self.context)

    def __getitem__(self, index):
        doc = self.context[index][0]
        if self.enable_scoring:
            score = self.context.get_score(index)
        else:
            score = None
        return self._translate(doc, score)

    # Internal methods
    def _translate(self, doc, score=None):
        attrs = self.indexer._translate_attributes(doc)
        if self.enable_scoring:
            if score is None:
                score = self.context.get_score(index)
            attrs['score'] = score
        return Hit(current=self.indexer.framework.fetch,
                   indexed=self.indexer.fetch, **attrs)
