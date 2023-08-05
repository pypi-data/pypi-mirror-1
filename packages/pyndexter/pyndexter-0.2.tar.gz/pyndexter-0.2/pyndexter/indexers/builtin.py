# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

"""
Builtin Indexer
---------------

The builtin Pyndexter indexer.

Pyndexter provides a basic inverted index indexer. It does not currently
support substring matching, wildcards, or scoring, but these features are
planned.

Usage
~~~~~

::

    builtin://<path>?compact=<bool>&cache=<bool>&dbm=<dbm>

``compact=<bool>`` (default: ``true``)
    Whether to compact the database as much as possible. Slight slowdown.

``cache=<bool>`` (default: ``false``)
    Should we keep a cached copy of each document as it is indexed?

``dbm=<dbm>`` (default: ``anydbm``)
    Supported dbm's are ``anydbm``, ``dbhash``, ``gdbm`` and ``dbm`` (Python 2.5).

Installation
~~~~~~~~~~~~

No installation is required. Pyndexter uses the anydbm Python module for
storage.
"""

import os
import re
import anydbm
import cPickle as pickle
import md5
from UserDict import DictMixin
from StringIO import StringIO
from gzip import GzipFile
from pyndexter import *
from pyndexter.util import set


class KeyedSet(object):
    def __init__(self, db):
        self.db = db

    def update(self, key, values):
        key = pickle.dumps(key, 2)
        try:
            v = pickle.loads(self.db[key])
        except KeyError:
            v = set()
        v.update(values)
        self.db[key] = pickle.dumps(v, 2)

    def remove(self, key, values=None):
        key = pickle.dumps(key, 2)
        if values is None:
            try:
                del self.db[key]
            except KeyError:
                pass
        else:
            try:
                v = pickle.loads(self.db[key])
                v.remove(values)
                self.db[key] = pickle.dumps(v, 2)
            except KeyError:
                pass

    def replace(self, key, values):
        key = pickle.dumps(key, 2)
        self.db[key] = pickle.dumps(values, 2)

    def get(self, key):
        key = pickle.dumps(key, 2)
        try:
            return pickle.loads(self.db[key])
        except KeyError:
            return set()

    def keys(self):
        for key in self.db.keys():
            yield pickle.loads(key)


class PickleDict(DictMixin):
    """A dictionary wrapper that automatically pickles keys and values."""
    def __init__(self, db):
        self.db = db

    def __getitem__(self, key):
        return pickle.loads(self.db[pickle.dumps(key, 2)])

    def __setitem__(self, key, value):
        self.db[pickle.dumps(key, 2)] = pickle.dumps(value, 2)

    def __delitem__(self, key):
        del self.db[pickle.dumps(key, 2)]

    def keys(self):
        return [pickle.loads(k) for k in self.db.keys()]


class BuiltinIndexer(Indexer):
    """Builtin Pyndexter indexer."""
    def __init__(self, framework, path, dbm='anydbm', cache=False,
                 compact=True):
        Indexer.__init__(self, framework)

        self.path = path
        self.compact = compact
        self.cache = cache
        self.state_path = os.path.join(path, 'store.db')
        self.db_path = os.path.join(path, 'builtin.db')

        # We want the minimum set of words
        framework.reduce.split = True
        framework.reduce.unique = True

        dbm = __import__(dbm, {}, {}, [''])

        if framework.mode == READWRITE:
            if not os.path.exists(self.db_path):
                os.makedirs(self.db_path)
            mode = 'c'
        else:
            mode = 'r'

        def dbopen(name):
            return dbm.open(os.path.join(self.db_path, name), mode)

        # wordid:set(uriid)
        self.words = KeyedSet(dbopen('words'))
        # uriid:set(wordid)
        self.uris = KeyedSet(dbopen('uris'))
        # uri:dict(attributes)
        self.attributes = PickleDict(dbopen('attributes'))

        if cache:
            self.cachedb = PickleDict(dbopen('cache'))

        if compact:
            # id:word mapping
            self.idword = PickleDict(dbopen('idword'))
            # word:id mapping
            self.wordid = PickleDict(dbopen('wordid'))
            # key:value config
            self.config = PickleDict(dbopen('config'))

            self.config.setdefault('wordid', 0)
        else:
            self._words = self._wids = lambda w: set(w)
            self._word = self._wid = lambda w: w

    def index(self, document):

        uri = unicode(self._wid(document.uri))
        words = self._wids(self.framework.reduce(document.content))
        doc_set = set([uri])

        if self.cache:
            if self.compact:
                # Do a low-compression gzip
                buffer = StringIO()
                gz = GzipFile(fileobj=buffer, compresslevel=1, mode='wb')
                gz.write(document.content.encode('utf-8'))
                gz.close()
                self.cachedb[uri] = buffer.getvalue()
            else:
                self.cachedb[uri] = document.content

        self.attributes[uri] = document.attributes

        old_words = self.words.get(document.uri)
        removed_words = old_words.difference(words)
        new_words = words.difference(old_words)

        # Clear out words that have been removed from the index
        for word in removed_words:
            self.words.remove(word, doc_set)

        # Add new words
        for word in new_words:
            self.words.update(word, doc_set)

        self.uris.replace(uri, words)

    replace = index

    def discard(self, uri):
        uri = unicode(uri)
        try:
            del self.attributes[uri]
        except KeyError:
            pass

        uri_set = set([uri])
        for word in self.uris.get(uri):
            self.uris.remove(word, uri_set)
        self.uris.remove(uri)

    def __iter__(self):
        for uri in self.uris.keys():
            yield URI(self._word(uri))

    def fetch(self, uri):
        uri = unicode(uri)
        uriid = self._wid(uri)
        attributes = self.attributes.get(uriid, {})
        attributes = dict([(k.encode('utf-8'), v)
                           for k, v in attributes.iteritems()])
        attributes['uri'] = uri
        if self.cache:
            content = self.cachedb[uriid]
            if self.compact:
                gz = GzipFile(fileobj=StringIO(content), mode='rb')
                content = gz.read().decode('utf-8')
            quality = 0.99
        else:
            content = ' '.join(self._words(self.uris.get(uriid)))
            quality = 0.1
        return Document(content=content, quality=quality, **attributes)

    def close(self):
        self.words = None
        self.uris = None
        self.attributes = None
        self.wordid = None
        self.idword = None
        self.config = None

    def search(self, query):
        query.reduce(self.framework.reduce)
        # FIXME NOT is not supported yet
        # FIXME Words without a WID can be automatically excluded from the
        # search

#        class invertedset(object):
#            def __init__(self, items=[]):
#                self.items = items
#
#            def intersection(self, other):
#                self.

        def visit(node):
            if node.type == node.TERM:
                return self.words.get(self._wid(node.value))
            elif node.type == node.AND:
                return visit(node.left).intersection(visit(node.right))
            elif node.type == node.OR:
                return visit(node.left).union(visit(node.right))
            elif node.type == node.NOT:
                raise NotImplementedError('NOT is ... not supported')
                #return invertedset(visit(node.left))

        uris = visit(query)
        return BuiltinResult(self, query, list(self._words(uris)))

    # Internal methods
    def _wids(self, words):
        """Convert a collection of words to a set of wids."""
        out = set()
        for word in words:
            out.add(self._wid(word))
        return out

    def _words(self, wids):
        """Convert a collection of wids to words."""
        out = set()
        for wid in wids:
            out.add(self.idword[wid])
        return out

    def _wid(self, word):
        """Return, or allocate, a unique word identifier."""
        try:
            return self.wordid[word]
        except KeyError:
            id = self.config['wordid']
            self.config['wordid'] = id + 1
            id = unicode(id)
            self.wordid[word] = id
            self.idword[id] = word
            return id

    def _word(self, wid):
        return self.idword[wid]


indexer_factory = PluginFactory(BuiltinIndexer, cache=bool, compact=bool)


class BuiltinResult(Result):
    def __iter__(self):
        for uri in self.context:
            yield self._translate(uri)

    def __getitem__(self, index):
        return self._translate(self.context[index])

    def _translate(self, uri):
        indexer = self.indexer
        framework = indexer.framework
        attributes = indexer.attributes.get(uri, {})
        attributes['uri'] = URI(uri)
        attributes = dict([(k.encode('utf-8'), v) for k, v in attributes.iteritems()])
        return Hit(current=framework.fetch, indexed=indexer.fetch, **attributes)
