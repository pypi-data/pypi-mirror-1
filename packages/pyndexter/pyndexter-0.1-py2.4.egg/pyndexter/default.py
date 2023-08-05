import re
import os
import anydbm
import cPickle as pickle
from copy import deepcopy
from pyndexter import *
from pyndexter.util import CacheDict
try:
    set = set
except NameError:
    from sets import Set as set


class PersistentDict(object):
    """ A persistent, lazy, caching, dictionary. Uses the anydbm module for
    persistence. """
    def __init__(self, file, mode='c', cache=2048):
        self._cache = CacheDict(cache)
        self._flush = {}
        self.mode = mode == READWRITE and 'c' or 'r'
        self.file = file
        self._dbm = anydbm.open(self.file, self.mode)

    def __contains__(self, key):
        key = key.encode('utf-8')
        return key in self._cache or key in self._dbm

    def __getitem__(self, key):
        key = key.encode('utf-8')
        if key in self._cache:
            return self._cache[key]
        return self._cache.setdefault(key, pickle.loads(self._dbm[key]))

    def __setitem__(self, key, value):
        key = key.encode('utf-8')
        self._cache[key] = self._flush[key] = value

    def __delitem__(self, key):
        found = False
        key = key.encode('utf-8')
        for data in (self._cache, self._flush, self._dbm):
            if key in data:
                del data[key]
                found = True
        if not found:
            raise KeyError(key)

    def keys(self):
        keys = set(self._cache.keys())
        keys.update(self._dbm.keys())
        return [key.decode('utf-8') for key in keys]

    def sync(self):
        for key, value in self._flush.iteritems():
            self._dbm[key] = pickle.dumps(value, 2)
        self._dbm.sync()
        self._flush = {}
        self._cache = {}


def synchronised(func):
    """ Locking decorator. """
    import pyndexter.portalocker as portalocker
    from time import strftime, localtime, time

    def synchronised(indexer, *args, **kwargs):
        if indexer._locked:
            return func(indexer, *args, **kwargs)

        if indexer.mode == READONLY:
            mode = portalocker.LOCK_SH
        else:
            mode = portalocker.LOCK_EX
        lockfile = open(indexer.lock_file, 'w+')
        portalocker.lock(lockfile, mode)
        # XXX This is not atomic
        indexer._locked = True
        lockfile.write(strftime('%x %X', localtime(time())))
        try:
            return func(indexer, *args, **kwargs)
        finally:
            indexer._locked = False
            lockfile.close()
    return synchronised


class DefaultIndexer(Indexer):
    """ Default indexer, using bigrams. """

    capabilities = CAP_READONLY | CAP_HITCOUNT | CAP_UNION | \
                   CAP_INTERSECTION | CAP_ITERATION | CAP_LIST | \
                   CAP_ATTRIBUTES | CAP_WHOLEWORD

    _tokeniser = re.compile(r'\w+')

    def __init__(self, path, source=None, mode=READWRITE, flush_every=128):
        Indexer.__init__(self, source, mode, os.path.join(path, 'state.db'))
        self.path = path
        self._init_env(self.path)
        self.lock_file = os.path.join(self.path, 'lock')
        self._locked = False
        self._open(mode)
        self._flush_every = flush_every
        self._index_count = 0

    def index(self, document):
        self._assert_rw()
        if isinstance(document, basestring):
            document = self.fetch(document)
        node_words = set()
        for word in set(self._tokeniser.findall(document.content)):
            word = u' ' + word + u' '
            # Split word into bigrams and add to the bigram LUT
            for bigram in self._bigram_word(word):
                if bigram in self.bigrams:
                    words = self.bigrams[bigram]
                    words.add(word)
                    self.bigrams[bigram] = words
                else:
                    self.bigrams[bigram] = set([word])

            # Update word:uri mapping
            if word in self.words:
                uris = self.words[word]
                uris.add(document.uri)
                self.words[word] = uris
            else:
                self.words[word] = set([document.uri])
            
            # Update attributes
            self.attributes[document.uri] = deepcopy(document.attributes)

        self.uris[document.uri] = node_words

        self._index_count += 1
        if not self._index_count % self._flush_every:
            self.words.sync()
            self.bigrams.sync()
            self.uris.sync()
            self.attributes.sync()
            
    index = synchronised(index)

    def discard(self, document):
        self._assert_rw()
        for word in self.uris[document.uri]:
            word_uris = self.words[word]
            word_uris.discard(document.uri)
            self.words[word] = word_uris
    discard = synchronised(discard)

    def search(self, phrase, flags=0, order_by=None, order_ascending=True,
               order_type=str):
        all_words = {}
        words = [word.lower() for word in phrase.split()]
        # First, find all possible words that each search word matches
        for idx, word in enumerate(words):
            if flags & SEARCH_WHOLEWORD:
                word = u' ' + word
                word = word + u' '
            words[idx] = word
            bigrams = self._bigram_word(word)
            all_words[word] = set([w for w in self._bigram_search(bigrams)
                                   if word in w])

#        # Next, find the intersection/union of all files that all words appear
#        # in
#        if flags & SEARCH_UNION:
#            all_uris = set()
#            for word in words:
#                all_files.update(self.words[fullword

        first_set = 1
        all_uris = set()
        for word in words:
            # Find all uris that word appears in
            word_uris = set()
            for fullword in all_words[word]:
                word_uris.update(set(self.words[fullword]))

            if first_set:
                all_uris = word_uris
                first_set = 0
            else:
                all_uris.intersection_update(word_uris)
        return DefaultSearch(self, phrase, all_uris)
    search = synchronised(search)

    def close(self):
        self.sync()
        self.words = self.bigrams = self.uris = None

    def sync(self):
        if self.mode == READWRITE:
            self.words.sync()
            self.bigrams.sync()
            self.uris.sync()
            self.attributes.sync()
            self._sync_source_state()
    sync = synchronised(sync)

    # Internal methods
    def _open(self, mode):
        # word:uri mapping
        self.words = PersistentDict(os.path.join(self.path, 'words.db'), mode, 8192)
        # bigram:word
        self.bigrams = PersistentDict(os.path.join(self.path, 'bigrams.db'), mode, 4096)
        # uri:words mapping
        self.uris = PersistentDict(os.path.join(self.path, 'uris.db'), mode, 32)
        # uri:attribute mapping
        self.attributes = PersistentDict(os.path.join(self.path, 'attributes.db'), mode, 32)
    _open = synchronised(_open)

    def _bigram_word(word):
        for start in range(0, len(word) - 1):
            yield word[start:start + 2]
    _bigram_word = staticmethod(_bigram_word)

    def _bigram_search(self, bigrams):
        """ Find all words containing matching bigrams. """
        first_hit = 1
        words = set()
        for bigram in bigrams:
            if bigram in self.bigrams:
                if first_hit:
                    words = self.bigrams[bigram]
                    first_hit = 0
                else:
                    words.intersection_update(set(self.bigrams[bigram]))
            else:
                return ()
        return words
    _bigram_search = synchronised(_bigram_search)


class DefaultSearch(Search):
    def __iter__(self):
        for uri in self.context:
            yield Hit(**self.indexer.attributes[uri])

    def __len__(self):
        return len(self.context)

    def __getitem__(self, index):
        return self.context[index]
