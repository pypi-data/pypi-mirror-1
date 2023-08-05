import os
import pickle
import gzip
from StringIO import StringIO
from urlparse import urlsplit, urlunsplit
try:
    set = set
except NameError:
    from sets import Set as set

__all__ = """
Error
InvalidURI
DocumentNotFound
InvalidMode
InvalidState
IndexerError
SourceError

REMOVED ADDED MODIFIED

READONLY READWRITE

CAP_READONLY CAP_ORDERING CAP_CONTENT CAP_ATTRIBUTES CAP_RELEVANCE CAP_HITCOUNT
CAP_LIST CAP_ITERATION CAP_ASTERISK CAP_QUESTION CAP_WHOLEWORD CAP_UNION
CAP_INTERSECTION

SEARCH_WHOLEWORD SEARCH_ASTERISK SEARCH_QUESTION SEARCH_UNION

Document Source Indexer Search Hit
""".split()

# Source state difference constants
REMOVED = 0
ADDED = 1
MODIFIED = 2

# Indexer open flags
READONLY = 0
READWRITE = 1

# Indexer capabilities
CAP_READONLY = 1        # Supports read-only access to the index
CAP_ORDERING = 2        # Supports result ordering
CAP_CONTENT = 4         # Can fetch() document content
CAP_ATTRIBUTES = 8      # Supports per-document attributes
CAP_RELEVANCE = 16      # Can return results by relevance
CAP_HITCOUNT = 32       # Search result supports len()
CAP_LIST = 64           # Search result supports list-style lookup
CAP_ITERATION = 128     # Supports index iteration
CAP_ASTERISK = 256      # Supports the asterisk wildcard (*<term>*)
CAP_QUESTION = 512      # Supports the single character wildcard (a?c)
CAP_WHOLEWORD = 512     # Performs whole word searches by default
CAP_UNION = 1024        # Supports unions (ie. matches documents with any word)
CAP_INTERSECTION = 2048 # Supports intersections (ie. matches documents with
                        # all words)

# Search flags. Flags may be ignored if the indexer does not support a
# particular feature.
SEARCH_WHOLEWORD = 1    # Perform a wholeword search
SEARCH_ASTERISK = 2     # Allow wildcard (*) in search term
SEARCH_QUESTION = 4     # Allow single character wildcard (?) in search term
SEARCH_UNION = 8        # Whether to perform a union rather than an
                        # intersection (the default) of search term results

class Error(Exception):
    """ Base of all pyndexter exceptions. """
class DocumentNotFound(Error):
    """ Raised when a document could not be found, usually by the fetch()
    methods. """
class InvalidURI(Error):
    """ The URI provided was invalid in that context. """
class SourceError(Error):
    """ Base of all exceptions raised exclusively by Sources. """
class InvalidState(SourceError):
    """ The state provided to a source was invalid. """
class IndexerError(Error):
    """ Base of all exceptions raised exclusively by Indexers. """
class InvalidMode(IndexerError):
    """ The mode (READONLY or READWRITE) of the indexer is an
    invalid state for a particular operation. """


class Document(object):
    """ A Document represents an indexable object in pyndexter. All string
    attributes must be unicode, including the content.
    
    content:: is optional, and if not provided will be fetched from the
    `source`. If it is a callable, it will be called to fetch the content,
    passing the uri as the only argument.

    change:: should be a numeric value representing the current point in the
    documents lifetime. Typically a timestamp, but could be a revision number,
    etc.
    
    source:: is the Source object where this documents content can be lazily
    fetched from. """

    __slots__ = ('attributes', '_content', 'source')

    def __init__(self, uri, content=None, source=None, changed=None,
                 **attributes):
        self._content = content
        self.source = source
        self.attributes = attributes
        self.attributes.update({'uri': uri, 'changed': changed})

    def __repr__(self):
        return '<Document "%s">' % self.uri

    def __getattr__(self, key):
        try:
            return self.attributes[key]
        except KeyError, e:
            raise AttributeError(unicode(e))

    def __hash__(self):
        return hash(self.uri)

    def _set_content(self, content):
        self._content = content

    def _get_content(self):
        if callable(self._content):
            self._content = self._content(self.uri)
        return self._content
    content = property(lambda self: self._get_content(),
                       lambda self, value: self._set_content(value))


class Source(object):
    """ A source of indexable documents. A Source object is responsible for not
    only fetching documents and iterating over them, but for determining what
    has changed in the source.
    
    Determing what has changed is achieved with the state() and difference()
    methods. The ''state'' of a source is the minimum information required to
    be able to determine what has changed. For FileSource this is a list of all
    files and their modification times, for a SubversionSource it would be as
    simple as the changeset number. The default state() and difference()
    methods use the data in self._state.

    (All attributes, including document contents and URI's must be in unicode)
    """

    def __init__(self, include=None, exclude=None, predicate=None):
        self.include = include or ['*']
        self.exclude = exclude or []
        self.predicate = predicate or self._glob_predicate
        self._state = {}

    def matches(self, uri):
        """ Does this source handle documents matching the given URI? (This
        method is primarily used by the MetaSource class) """
        raise NotImplementedError

    def __hash__(self):
        """ The hash must uniquely identify the source. (This
        method is primarily used by the MetaSource class) """
        raise NotImplementedError('The hash of a Source is required by the '
                                  'MetaSource class.')

    def __iter__(self):
        """ Iterate over all *valid* URI's in this source. """
        raise NotImplementedError

    def fetch(self, uri):
        """ Fetch a document identified by uri. Ideally the Document object
        returned would not have the content included, but would pass a callable
        to the Document constructor that can fetch it. Should raise
        DocumentNotFound if unable to fetch the document. """
        raise NotImplementedError

    def exists(self, uri):
        """ Does the document exist at `uri`? """
        try:
            self.fetch(uri)
            return True
        except DocumentNotFound:
            return False

    def state(self):
        """ Return a raw byte string representing the current state of this
        source.  Storage and retrieval of this byte string is typically handled
        by the Indexer. If this method returns false, the Indexer will assume
        that state information is not available, and do nothing. """
        if not self._state:
            return None
        return self._marshal_state(self._state)

    def difference(self, state):
        """ Return an iterable of tuples representing the differences between
        the current state of the source and that in the provided state. Each
        tuple is in the form `(<transition>, uri)`, where <transition> is one
        of ADDED, REMOVED or MODIFIED. """
        current = set()
        state = self._unmarshal_state(state)
        for uri in self:
            current.add(uri)
            if uri not in state:
                yield (ADDED, uri)
            elif self.fetch(uri).changed != state[uri]:
                yield (MODIFIED, uri)
        for removed in set(state.keys()).difference(current):
            yield (REMOVED, removed)

    # Useful helper methods
    def _glob_predicate(self, uri):
        """ Given a list of include and exclude pattern lists, return whether
        the given uri matches. """
        from fnmatch import fnmatch
        for pattern in self.exclude:
            if fnmatch(uri, pattern):
                return False
        for pattern in self.include:
            if fnmatch(uri, pattern):
                return True
        return False

    def _marshal_state(self, state):
        """ Pickle and compress state. This is used by the default state()
        implementation, but can be reused. """
        state = pickle.dumps(state, 2)
        compressed = StringIO()
        gzip.GzipFile(filename='pyndexer source state', fileobj=compressed,
                      mode='wb', compresslevel=1).write(state)
        return compressed.getvalue()

    def _unmarshal_state(self, state):
        """ Uncompress and unpickle state. Used by the default difference()
        method, but can be reused. """
        state = StringIO(state)
        try:
            ungzipped = gzip.GzipFile(fileobj=state, mode='rb').read()
            return pickle.loads(ungzipped)
        except Exception, e:
            raise InvalidState('Invalid state provided to document source. '
                               'Exception was %s: %s' % (e.__class__.__name__, e))

class Indexer(object):
    capabilities = 0

    """ An Indexer performs indexing and searching on a document Source.
    
    `source` is the Source object, if any.
    `state_path` is the location to store `source` state data. If this is
    provided, update() and sync() will automatically store and retrieve source
    state. """
    def __init__(self, source=None, mode=READWRITE, state_path=None):
        self.source = source
        self.mode = mode
        self.state_path = state_path

    def fetch(self, uri):
        """ Fetch a document. Try to use the indexers data, but fall back
        on the Source copy, if available. """
        if not self.source:
            raise IndexerError("This indexer has no associated Source object "
                               "and as such can not fetch() documents.")
        return self.source.fetch(uri)

    def __iter__(self):
        """ Iterate over all URI's in the index. """
        raise NotImplementedError

    def update(self):
        """ Update the index with the current state of the document source. """
        self._assert_rw()
        if not self.source:
            raise IndexerError("Can't perform automatic update without a Source.")
        if not self.state_path:
            raise IndexerError("Source state path not set, Indexer is not "
                               "capable of automatic updates.")
        if os.path.exists(self.state_path):
            try:
                state = open(self.state_path).read()
            except Exception, e:
                raise IndexerError("Source state '%s' is not readable. "
                                   "Exception was %s: %s" % 
                                   (self.state_path, e.__class__.__name__,
                                    unicode(e)))

            for transition, uri in self.source.difference(state):
                if transition == REMOVED:
                    self.discard(uri)
                else:
                    self.index(uri)
        else:
            for uri in self.source:
                self.index(uri)

    def index(self, document):
        """ Index a single document, specified as either a Document object
        or a URI. """
        raise NotImplementedError

    def discard(self, document):
        """ Discard the specified document from the index, specified as either
        a Document object or a URI. """
        raise NotImplementedError

    def search(self, phrase, flags=0, order_by=None,
               order_ascending=True, order_type=str):
        """ Search the index for documents containing the given terms. If
        intersection is True, return only documents that match all terms. This
        method is guaranteed to work across all indexers.
        
        `order` is an optional attribute by which to order results. If prefixed
        by a `<`, results will be in descending order, `>` for ascending.

        `order_type` is typically either `str` or `int`.

        `flags` is a bitwise or of the `SEARCH_*` flags
        
        Returns a Search object. """
        raise NotImplementedError

    def close(self):
        """ Sync and close the indexer. The object is subsequently not
        usable. """
        raise NotImplementedError

    # Default NOP methods
    def optimize(self):
        """ Optimise the indexer. """

    def sync(self):
        """ Synchronise indexer with on-disk representation. """

    # Helper methods
    def _assert_rw(self):
        if self.mode != READWRITE:
            raise InvalidMode("%s must be in READWRITE mode for this "
                              "operation" % self.__class__.__name__)

    def _sync_source_state(self):
        """ Save Source objects state to the location defined in the
        constructor. """
        if self.mode == READWRITE and self.source and self.state_path:
            state = self.source.state()
            if state:
                open(self.state_path, 'w').write(self.source.state())

    def _init_env(self, path):
        """ Create a default environment with a <path> base directory. """
        if not os.path.exists(path):
            if self.mode != READWRITE:
                raise IndexError("Indexer environment has not been initialised")
            os.makedirs(path)

class Search(object):
    """ Represents the result of a search. Each hit is returned as a Hit
    object. """

    def __init__(self, indexer, phrase, context):
        self.indexer = indexer
        self.phrase = phrase
        self.context = context

    def __iter__(self):
        """ Return an iterator over the result set, returning a Hit object for
        each matching document. """
        raise NotImplementedError

    def __len__(self):
        """ Return the length of the result set. """
        raise NotImplementedError

    def __getitem__(self, index):
        """ Return a Hit object for a specific index in the search result. Not
        necessarily implemented by all Indexers. """
        raise NotImplementedError

    def __getslice__(self, i, j):
        """ Return an iterator over a slice of the search set. """
        for idx in xrange(i, j):
            yield self[idx]


class Hit(object):
    """ Wrapper around a search hit. If `document` is a callable, it should
    be a function that fetches the Document associated with `uri`, which is
    passed as the only argument. """

    __slots__ = ('attributes', '_document')

    def __init__(self, uri, document=None, score=None, **attributes):
        self._document = document
        self.attributes = attributes
        self.attributes.update({'uri': uri, 'score': score})

    def __getattr__(self, key):
        try:
            return self.attributes[key]
        except KeyError, e:
            raise AttributeError(unicode(e))

    def _get_document(self):
        if callable(self._document):
            self._document = self._document(self.uri)
        return self._document
    document = property(_get_document)
