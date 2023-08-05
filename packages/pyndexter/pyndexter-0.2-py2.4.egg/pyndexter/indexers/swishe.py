# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import SwishE
from pyndexter import *

"""
Swish-e
-------

`Siwsh-e <http://swish-e.org/>`_ is a popular indexer, typically used for internal web sites.

This is a search-only adapter, implemented via the SwishE_ Python module (which
doesn't appear to support indexing?). Indexing still has to be performed by
Swish-e itself.

Usage
~~~

::

    swishe://<path>

Installation
~~~~~~~~~~

::

    easy_install SwishE

.. _SwishE: http://jibe.freeshell.org/bits/SwishE/
"""

class SwishEIndexer(Indexer):
    def __init__(self, framework, path):
        Indexer.__init__(self, framework)
        self.path = path
        self.db = SwishE.new(path)

    def search(self, query):
        results = self.db.query(query.phrase)
        return SwishEResult(self, query, results)


class SwishEResult(Result):
    def __iter__(self):
        for row in self.context:
            uri = row.getproperty('swishdocpath')
            yield Hit(current=self.indexer.framework.fetch,
                      indexed=self.indexer.fetch, uri=uri)

    def len(self):
        return self.context.hits()

indexer_factory = PluginFactory(SwishEIndexer)
