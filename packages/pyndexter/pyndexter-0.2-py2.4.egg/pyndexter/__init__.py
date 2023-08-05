# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#


"""
Pyndexter provides a uniform API for accessing a variety of full-text
indexing engines. It is similar in purpose to the Python DB API.

The main class users will be dealing with is Framework. This class
ties indexers and sources of documents together and provides a mechanism
for performing automatic updates.

An example of indexing all .txt files underneath ``/usr/share/doc``:

::

    import os
    from pyndexter import Framework

    framework = Framework('hyperestraier:///tmp/hyperestraier.idx')
    framework.add_source('file:///usr/share/doc?include=*.txt')

    framework.update()

    # Find all documents with Linus and Torvalds in them
    for hit in framework.search('Linus Torvalds'):
        print hit.uri

    framework.close()
"""


import re
import os
import pickle
import gzip
import inspect
from StringIO import StringIO
from urlparse import urlsplit, urlunsplit
from pyndexter.util import set, URI


__version__ = '0.2'
__author__ = 'Alec Thomas <alec@swapoff.org>'


__all__ = """
Error
InvalidURI
DocumentNotFound
InvalidMode
InvalidState
IndexerError
SourceError
InvalidQuery

REMOVED ADDED MODIFIED

READONLY READWRITE

Query Framework Document Source Indexer Result StateStore Hit PluginFactory URI
Excerpt
""".split()


# Source state difference constants
REMOVED = 0
ADDED = 1
MODIFIED = 2

# Indexer open flags
READONLY = 0
READWRITE = 1


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

class InvalidQuery(Error):
    """ Invalid query string. """

class FrameworkError(Error):
    """Base of Framework errors."""

class InvalidModule(FrameworkError):
    """The module provided was not loadable."""
    def __init__(self, module, exception=None):
        message = 'Could not load module "%s"' % module
        if exception:
            message += '. Original exception was: %s' % exception
        FrameworkError.__init__(self, message)


class Document(object):
    """ A Document represents an indexable object in pyndexter. All string
    attributes must be unicode, including the content.

    ``content``
        Optional, and if not provided will be fetched from the `source`. If it
        is a callable, it will be called to fetch the content, passing the uri
        as the only argument.

    ``change``
        Should be a numeric value representing the current point in the
        documents lifetime. Typically a timestamp, but could be a revision
        number, etc.

    ``source``
        Is the Source object where this documents content can be lazily fetched
        from. """

    __slots__ = ('attributes', '_content', 'source', 'quality')

    def __init__(self, uri, content=None, source=None, changed=None,
                 quality=1.0, **attributes):
        self._content = content
        self.source = source
        self.quality = quality
        self.attributes = attributes
        self.attributes.update({'uri': URI(uri), 'changed': changed})

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            ' '.join(['%s=%s' % (k, repr(v)) for k, v in
                                      self.attributes.iteritems()]))

    def __getattr__(self, key):
        try:
            return self.attributes[key]
        except KeyError, e:
            raise AttributeError(unicode(e))

    def __contains__(self, key):
        return key in self.attributes

    def __hash__(self):
        return hash(self.uri)

    def get(self, key, default=None):
        return self.attributes.get(key, default)

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
    methods. The `state` of a source is the minimum information required to
    be able to determine what has changed. For FileSource this is a list of all
    files and their modification times, for a SubversionSource it would be as
    simple as the changeset number. By default, ``marshal()`` and
    ``difference()`` assume that ``_state`` will contain a dictionary of
    uri:modification-time mappings.

    All URI's passed to and from Source objects must be `URI` objects.

    (All attributes, including document contents and URI's must be in unicode)
    """

    def __init__(self, framework, include=None, exclude=None, predicate=None):
        if include is None and exclude is None:
            include = ['*']
            exclude = []
        elif include is None:
            include = []
        elif exclude is None:
            exclude = []
        self.framework = framework
        self.include = include
        self.exclude = exclude
        self.predicate = predicate or self._glob_predicate
        self._state = {}

    def matches(self, uri):
        """ Does this source handle documents matching the given URI? (This
        method is primarily used by the MetaSource class) """
        raise NotImplementedError

    def __hash__(self):
        """ The hash must uniquely identify the source. (This method is
        primarily used by the MetaSource class) """
        raise NotImplementedError

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

    def marshal(self, file):
        """ Store the state of the `Source` to `file`. Used during an
        `update()`. """
        state = pickle.dumps(self._state, 2)
        gzip.GzipFile(filename='pyndexter source state', fileobj=file,
                      mode='wb', compresslevel=1).write(state)

    def difference(self, file):
        """ Return an iterable of tuples representing the differences between
        the current state of the `Source` and that in the provided state. Each
        tuple is in the form `(<transition>, uri)`, where <transition> is one
        of `ADDED`, `REMOVED` or `MODIFIED` and uri is a URI object."""
        current = set()
        try:
            ungzipped = gzip.GzipFile(fileobj=file, mode='rb').read()
            state = pickle.loads(ungzipped)
        except Exception, e:
            raise InvalidState('Invalid state provided to document source. '
                               'Exception was %s: %s' % (e.__class__.__name__, e))
        for uri in self:
            uuri = unicode(uri)
            current.add(uuri)
            if uuri not in state:
                yield (ADDED, uri)
            elif self.fetch(uri).changed != state[uuri]:
                yield (MODIFIED, uri)
        for removed in set(state.keys()).difference(current):
            yield (REMOVED, URI(removed))

    # Useful helper methods
    def _glob_predicate(self, uri):
        """ Given a list of include and exclude pattern lists, return whether
        the given uri matches. """
        uri = unicode(uri)
        from fnmatch import fnmatch
        for pattern in self.exclude:
            if fnmatch(uri, pattern):
                return False
        for pattern in self.include:
            if fnmatch(uri, pattern):
                return True
        return False


class QueryNode(object):
    """A query parse node.

    >>> QueryNode(QueryNode.TERM, 'one')
    ("one")
    >>> QueryNode(QueryNode.AND,
    ...     left=QueryNode(QueryNode.TERM, 'one'),
    ...     right=QueryNode(QueryNode.TERM, 'two'))
    (and
      ("one")
      ("two"))
    >>> QueryNode(QueryNode.NOT, left=QueryNode(QueryNode.TERM, 'one'))
    (not
      ("one")
      nil)
    """


    NULL = 0
    TERM = 1
    NOT = 2
    AND = 3
    OR = 4

    __slots__ = ('type', 'value', 'left', 'right')

    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        type_map = ('null', 'term', 'not', 'and', 'or')
        def show(node, depth=0):
            if node.type == QueryNode.TERM:
                text = '%s("%s"' % ('  ' * depth, node.value)
            else:
                text = "%s(%s%s" % ('  ' * depth, type_map[node.type], node.value and ' "%s"' % node.value or "")
            if node.left or node.right:
                text += "\n"
                if node.left:
                    text += show(node.left, depth + 1)
                else:
                    text += "%snil" % ('  ' * (depth + 1))
                text += "\n"
                if node.right:
                    text += show(node.right, depth + 1)
                else:
                    text += "%snil" % ('  ' * (depth + 1))
            text += ")"
            return text
        return show(self)


class Query(QueryNode):
    """ Query parser. Converts a simple query language into a parse tree which
    Indexers can then convert into their own implementation-specific
    representation.

    The query language is in the following form:

        <term> <term>     document must contain all of these terms
        "some term"       return documents matching this exact phrase
        -<term>           exclude documents containing this term
        <term> or <term>  return documents matching either term

    eg.

    >>> Query('lettuce tomato -cheese')
    (and
      ("lettuce")
      (and
        ("tomato")
        (not
          ("cheese")
          nil)))

    >>> Query('"mint slices" -timtams')
    (and
      ("mint slices")
      (not
        ("timtams")
        nil))

    >>> Query('"brie cheese" or "camembert cheese"')
    (or
      ("brie cheese")
      ("camembert cheese"))

    """

    _tokenise_re = re.compile(r"(?P<ex>-)|(?P<or>or)|\"(?P<dq>(?:\\.|[^\"])*)\"|'(?P<sq>(?:\\.|[^'])*)'|(?P<te>(?:\S)+)", re.I)
    _group_map = {'dq': QueryNode.TERM, 'sq': QueryNode.TERM, 'te': QueryNode.TERM,
                  'ex': QueryNode.NOT, 'or': QueryNode.OR}

    def __init__(self, phrase):
        QueryNode.__init__(self, None)
        tokens = self._tokenise(phrase)
        root = self.parse(tokens)
        self.phrase = phrase
        self._compiled = None
        if root:
            # Make ourselves into the root node
            for k in self.__slots__:
                setattr(self, k, getattr(root, k))

    def parse(self, tokens):
        # TODO: add support for sub-expressions eg. "(a b) or c"
        left = self.parse_unary(tokens)
        if tokens:
            if tokens[0][0] == QueryNode.OR:
                tokens.pop(0)
                return QueryNode(QueryNode.OR, left=left, right=self.parse(tokens))
            else:
                return QueryNode(QueryNode.AND, left=left, right=self.parse(tokens))
        return left

    def parse_unary(self, tokens):
        """Parse a unary operator. Currently only NOT.

        >>> q = Query('')
        >>> q.parse_unary(q._tokenise('-foo'))
        (not
          ("foo")
          nil)
        """
        if not tokens:
            return None
        if tokens[0][0] == QueryNode.NOT:
            tokens.pop(0)
            return QueryNode(QueryNode.NOT, left=self.parse_terminal(tokens))
        return self.parse_terminal(tokens)

    def parse_terminal(self, tokens):
        """Parse a terminal token.

        >>> q = Query('')
        >>> q.parse_terminal(q._tokenise('foo'))
        ("foo")
        """

        if not tokens:
            raise InvalidQuery('Unexpected end of string')
        if tokens[0][0] in (QueryNode.TERM, QueryNode.OR):
            token = tokens.pop(0)
            return QueryNode(QueryNode.TERM, value=token[1])
        raise InvalidQuery('Expected terminal, got "%s"' % tokens[0][1])

    def terms(self, exclude_not=True):
        """A generator returning the terms contained in the Query."""
        def _convert(node):
            if not node:
                return
            if node.type == node.TERM:
                yield node.value
            elif node.type == node.NOT and exclude_not:
                return
            else:
                for child in _convert(node.left):
                    yield child
                for child in _convert(node.right):
                    yield child

        return _convert(self)

    def __call__(self, text):
        """Match the query against a block of text. The Query will be lazily
        compiled to Python code."""
        import compiler
        from compiler import ast, misc, pycodegen

        def _generate(node):
            if node.type == node.TERM:
                return ast.Compare(ast.Const(node.value.lower()),
                                   [('in', ast.Name('text'))])
            elif node.type == node.AND:
                return ast.And([_generate(node.left), _generate(node.right)])
            elif node.type == node.OR:
                return ast.Or([_generate(node.left), _generate(node.right)])
            elif node.type == node.NOT:
                return ast.Not(_generate(node.left))
            else:
                raise NotImplementedError

        qast = ast.Expression(ast.Lambda(['text'], [], 0, _generate(self)))
        misc.set_filename('<%s compiled query>' % self.__class__.__name__,
                          qast)
        gen = pycodegen.ExpressionCodeGenerator(qast)
        self.__call__ = eval(gen.getCode())
        return self.__call__(text)

    def as_string(self, and_=' AND ', or_=' OR ', not_='NOT '):
        """Convert Query to a boolean expression. Useful for indexers with
        "typical" boolean query syntaxes.

        eg. "term AND term OR term AND NOT term"

        The expanded operators can be customised for syntactical variations.

        >>> Query('foo bar').as_string()
        'foo AND bar'
        >>> Query('foo bar or baz').as_string()
        'foo AND bar OR baz'
        >>> Query('foo -bar or baz').as_string()
        'foo AND NOT bar OR baz'
        """
        def _convert(node):
            if not node or node.type == node.NULL:
                return ''
            if node.type == node.AND:
                return '%s%s%s' % (_convert(node.left), and_,
                                   _convert(node.right))
            elif node.type == node.OR:
                return '%s%s%s' % (_convert(node.left), or_,
                                   _convert(node.right))
            elif node.type == node.NOT:
                return '%s%s' % (not_, _convert(node.left))
            elif node.type == node.TERM:
                return node.value
            else:
                raise NotImplementedError
        return _convert(self)

    def reduce(self, reduce):
        """Pass each TERM node through `Reducer`."""
        def _reduce(node):
            if not node:
                return
            if node.type == node.TERM:
                node.value = reduce(node.value, unique=False, split=False)
            _reduce(node.left)
            _reduce(node.right)
        _reduce(self)

    # Internal methods
    def _tokenise(self, phrase):
        """Tokenise a phrase string.

        >>> q = Query('')
        >>> q._tokenise('one')
        [(1, 'one')]
        >>> q._tokenise('one two')
        [(1, 'one'), (1, 'two')]
        >>> q._tokenise('one or two')
        [(1, 'one'), (4, 'or'), (1, 'two')]
        >>> q._tokenise('"one two"')
        [(1, 'one two')]
        >>> q._tokenise("'one two'")
        [(1, 'one two')]
        >>> q._tokenise('-one')
        [(2, '-'), (1, 'one')]
        """
        tokens = [(self._group_map[token.lastgroup], token.group(token.lastindex))
                  for token in self._tokenise_re.finditer(phrase)]
        return tokens


class Reducer(object):
    """Compact all words in a block of text."""

    def __init__(self, words_re=re.compile(r'\w+'), stemmer=lambda w: w,
                 min_word_length=3, max_word_length=64, unique=False,
                 split=False, lower=True):
        """`words_re` is a regular expression object or string.

        `stemmer` is a callable that stems a single word.

        If `unique` is true, return a string of **unordered** words with
        duplicates removed.

        If `split` is true, return words in a collection rather than joining
        them into a single string.

        If `lower` is true, lowercase text."""

        if isinstance(words_re, basestring):
            words_re = re.compile(words_re, re.UNICODE)
        self.words_re = words_re
        self.stemmer = stemmer
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.unique = unique
        self.split = split
        self.lower = lower

    def __call__(self, text, unique=None, split=None):
        if unique is None:
            unique = self.unique

        if unique:
            out = set()
            def append(word):
                out.add(word)
        else:
            out = []
            def append(word):
                out.append(word)

        min = self.min_word_length
        max = self.max_word_length
        stemmer = self.stemmer

        if self.lower:
            text = text.lower()

        words = self.words_re.findall(text)
        if unique:
            words = set(words)

        for word in words:
            if min > len(word) > max:
                continue
            append(stemmer(word))

        if split is None:
            split = self.split
        if split:
            return out
        return u' '.join(out)


class StateStore(object):
    """A class providing file-like objects for storage and retrieval of
    framework state."""

    def __init__(self, path):
        self.path = path

    def store(self):
        """Return a file-like object for storing state."""
        return open(self.path, 'wb')

    def retrieve(self):
        """Return a file-like object for fetching state."""
        return open(self.path, 'rb')

    def exists(self):
        """Does the state store exist?"""
        return os.path.exists(self.path)


class Indexer(object):
    """An Indexer performs document indexing and searching. This base object
    provides a framework for indexers."""

    def __init__(self, framework):
        """ Initialise indexer. """
        self.framework = framework

    def close(self):
        """ Close the indexer. The object is subsequently not usable.

        `flush()` is automatically called by the `Framework` prior to
        `close()`."""
        raise NotImplementedError

    def index(self, document):
        """ Index a single Document object. """
        raise NotImplementedError

    def discard(self, uri):
        """ Discard a document. """
        raise NotImplementedError

    def search(self, query):
        """ Search with the given Query. """
        # TODO Add support for result ordering
        raise NotImplementedError

    # Optional methods
    def __iter__(self):
        """ Iterate over all URI's in the index. """
        raise NotImplementedError

    def fetch(self, uri):
        """Attempt to fetch indexer representation of the document.

        Must return a `Document` object with a `quality` attribute between 0.0
        and 1.0, representing the quality of the document in comparison to the
        original."""
        raise DocumentNotFound(uri)

    def replace(self, document):
        """Replace a document in the index. Default is to `discard()` and
        `index()`."""
        self.discard(document.uri)
        self.index(document)

    def optimise(self):
        """ Optimise the indexer. """

    def flush(self):
        """Flush indexer state to disk."""

    def state_store(self):
        """If this Indexer is capable of storing framework state, return a
        `StateStore` object. By default, if the indexer has a `state_path`
        attribute, a new `StateStore` object will be returned on that path."""
        if hasattr(self, 'state_path'):
            return StateStore(self.state_path)
        return None


class PluginFactory(object):
    """Factory for translating URL-style query parameters into a standard
    plugin constructor call.

    >>> class C:
    ...   def __init__(self, one, two, three=3):
    ...     print one, two, three
    >>> f = PluginFactory(C, three=int, four="three")
    >>> c = f(one=1, two=2, three=3)
    1 2 3
    >>> c = f(uri='scheme://?one=1&two=2&three=three')
    Traceback (most recent call last):
    ...
    ValueError: could not coerce argument "three" with value "three" to type "<type 'int'>": invalid literal for int(): three
    >>> c = f(uri='scheme://?one=1&two=2&four=3')
    1 2 3
    """

    BOOL_TRUE = ('1', 'true', 'yes', 'on', 'aye')

    class List(object):
        """Translate a parameter that is a list of elements of `type`,
        optionally splitting on commas."""
        def __init__(self, type, split=None):
            self.type = type
            self.split = split

        def __call__(self, value):
            if self.split:
                out = []
                for v in value:
                    split_out += i.split(',')
                return split_out
            else:
                return [self.type(v) for v in value]

    def __init__(self, plugin, **arg_types):
        """Create a new factory.

        arg_types is a dictionary of <arg>:<type> mappings. If <type> is a
        string, <arg> will be renamed to this before calling the plugin
        constructor."""

        self.plugin = plugin
        self.remapped = dict([(k, v) for k, v in arg_types.iteritems()
                              if isinstance(v, basestring)])
        self.arg_types = arg_types
        args, varargs, self.varkw, defaults = \
            inspect.getargspec(self.plugin.__init__)
        defaults = defaults or []
        self.defaults = dict(zip(list(args[-len(defaults):]), defaults))
        self.defaults.pop('self', None)
        self.args = defaults and args[:-len(defaults)] or args

    def __call__(self, uri=None, **kwargs):
        args = dict(self.defaults.items())

        if uri is not None:
            # Merge URI arguments
            if isinstance(uri, basestring):
                from pyndexter.util import URI
                uri = URI(uri)

            uri.username = uri.username or None
            uri.password = uri.password or None
            uri_components = {'username': uri.username, 'password': uri.password,
                              'host': uri.host, 'path': uri.path,
                              'fragment': uri.fragment}
            # Discard them if they're empty
            uri_components = dict([(k, v) for k, v in uri_components.iteritems() if v])
            args.update(uri.query)
            args.update(uri_components)

        # Add keyword arguments
        args.update(kwargs)

        # Remap (rename) arguments
        for k, v in self.remapped.iteritems():
            if k in args:
                args[v] = args[k]
                del args[k]

        # Translate all remaining arguments
        for k, v in args.items():
            if v is not None:
                type = self.arg_types.get(k, lambda v: v)
                # If it's a list, and not marked as such, convert it to a scalar
                if isinstance(v, (tuple, list)) and not \
                        isinstance(type, self.List):
                    if len(v) != 1:
                        raise ValueError('argument "%s" should be a scalar' % k)
                    v = v[0]
                if type is bool:
                    # Special-case bool
                    if str(v) in self.BOOL_TRUE:
                        args[k] = True
                    else:
                        try:
                            args[k] = bool(float(v))
                        except ValueError:
                            args[k] = False
                else:
                    try:
                        args[k] = type(v)
                    except ValueError, e:
                        raise ValueError('could not coerce argument "%s" with '
                                         'value "%s" to type "%s": %s'
                                         % (k, v, type, e))

        return self.plugin(**args)


class Framework(object):
    """The glue. Ties `Indexer` and `Source` together, performs housekeeping
    tasks and provides a convenient interface to it all.

    If the `Indexer` is not capable of storing state and automatic updates are
    desired, a `StateStore` object should be passed to the `Framework`."""

    def __init__(self, indexer=None, mode=READWRITE, state_store=None,
                 reduce=None, stemmer=None):
        """`indexer` is a URI used to construct an indexer, or an `Indexer`
        object.

        `reduce` is a `Reducer` object.If `reduce` is not specified, a default
        `Reduce` object will be instantiated using `stemmer` (URI or callable)
        as defaults. '''NOTE:''' Use of the reducer is optional - some
        indexers may implement stemming and reduction internally."""
        self.mode = mode

        if reduce is None:
            if stemmer is None:
                stemmer = lambda word: word
            elif isinstance(stemmer, (basestring, URI)):
                Stemmer = self._load_plugin('stemmer', stemmer)
                stemmer = Stemmer(uri=stemmer)
            self.reduce = Reducer(stemmer=stemmer)
        else:
            self.reduce = reduce

        self.state_store = state_store
        self.indexer = indexer

        from pyndexter.sources.metasource import MetaSource
        self.source = MetaSource(self)

    def set_indexer(self, indexer):
        """Set the `Framework` indexer. Can either be a URI or an `Indexer`
        object."""
        if isinstance(indexer, (basestring, URI)):
            Indexer = self._load_plugin('indexer', indexer)
            self._indexer = Indexer(framework=self, uri=indexer)
        else:
            self._indexer = indexer

        if self.state_store is None:
            self.state_store = self.indexer.state_store()

    def get_indexer(self):
        return self._indexer

    indexer = property(get_indexer, set_indexer)

    def add_source(self, source):
        """ Add a source to be indexed to the framework. Can either be a
        `Source` instance or a URI."""
        if isinstance(source, (basestring, URI)):
            Source = self._load_plugin('source', source)
            source = Source(framework=self, uri=source)
        self.source.add_source(source)

    def fetch(self, uri):
        """ Fetch a document. """
        uri = URI(uri)
        return self.source.fetch(uri)

    def __iter__(self):
        """ Iterate over all URI's in the document source. """
        for uri in self.source:
            yield uri

    def update(self, filter=None, context=None):
        """ Update the index with the current state of the document source.

        `filter` is a callable in the form `(framework, context, stream)`,
        where `stream` is an iterable of `(transition, uri)` pairs."""
        self._assert_rw()
        if not self.state_store:
            raise IndexerError("Indexer not capable of storing source state, "
                               "and store not provided to Framework - not "
                               "capable of automatic updates.")
        if not filter:
            def filter(framework, context, stream):
                for transition, uri in stream:
                    yield transition, uri

        if self.state_store.exists():
            store = self.state_store.retrieve()
            for transition, uri in filter(self, context,
                                          self.source.difference(store)):
                if transition == REMOVED:
                    self.discard(uri)
                elif transition == MODIFIED:
                    self.replace(uri)
                else:
                    self.index(uri)
        else:
            def fake_difference():
                for uri in self.source:
                    yield ADDED, uri

            for transition, uri in filter(self, context, fake_difference()):
                self.index(uri)
        self.flush()

    def index(self, document):
        """Index a single document, specified as either a Document object or a
        URI."""
        self._assert_rw()
        if isinstance(document, (URI, basestring)):
            document = self.fetch(document)
        return self.indexer.index(document)

    def discard(self, document):
        """Discard the specified document from the index, specified as either a
        Document object or a URI."""
        self._assert_rw()
        if isinstance(document, Document):
            document = document.uri
        return self.indexer.discard(document)

    def replace(self, document):
        """Replace document in the index, specified as either a Document object
        or a URI."""
        self._assert_rw()
        if isinstance(document, (URI, basestring)):
            document = self.fetch(document)
        return self.indexer.replace(document)

    def search(self, query):
        """ Search the index for documents matching the given query.  This
        method is guaranteed to work across all indexers.

        `query` is a pyndexter compatible search string.

        Returns a `Result` object. """
        if isinstance(query, basestring):
            query = Query(query)
        return self.indexer.search(query)

    def close(self):
        """ Sync and close the indexer. The object is subsequently not
        usable. """
        self.flush()
        self.indexer.close()

    def optimise(self):
        """ Optimise the indexer. """
        self.indexer.optimise()

    def flush(self):
        """Flush indexer state to disk."""
        if self.mode == READWRITE:
            if self.mode == READWRITE and self.state_store:
                store = self.state_store.store()
                self.source.marshal(store)
            self.indexer.flush()

    # Helper methods
    def _load_plugin(self, type, uri):
        from pyndexter.util import URI
        uri = URI(uri)
        try:
            module_name = 'pyndexter.%ss.%s' % (type, uri.scheme)
            module = __import__(module_name, {}, {}, [''])
        except ImportError, e:
            raise InvalidModule(module_name, e)
        indexer_factory = getattr(module, type + '_factory')
        assert isinstance(indexer_factory, PluginFactory)
        return indexer_factory

    def _assert_rw(self):
        if self.mode != READWRITE:
            raise InvalidMode("%s must be in READWRITE mode for this "
                              "operation" % self.__class__.__name__)


class Result(object):
    """Represents the result of a search. Each hit is returned as a Hit
    object."""

    def __init__(self, indexer, query, context):
        self.indexer = indexer
        self.query = query
        self.context = context

    def __iter__(self):
        """Return an iterator over the result set, returning a Hit object
        for each matching document."""
        raise NotImplementedError

    def __len__(self):
        """ Return the length of the result set. """
        raise NotImplementedError

    def __getitem__(self, index):
        """Return a Hit object for a specific index in the search result.
        Not necessarily implemented by all Indexers."""
        raise NotImplementedError

    def __getslice__(self, i, j):
        """ Return an iterator over a slice of the search set. """
        for idx in xrange(i, j):
            try:
                yield self[idx]
            except (IndexError, NotImplementedError):
                break


class Hit(object):
    """ Wrapper around a search hit. If `current` is a callable, it should
    be a function that fetches the Document associated with `uri`, which is
    passed as the only argument. """

    __slots__ = ('attributes', '_current', '_indexed')

    def __init__(self, uri, current=None, indexed=None, **attributes):
        self._current = current
        self._indexed = indexed
        self.attributes = attributes
#        if isinstance(uri, basestring):
#            from pyndexter.util import URI
#            uri = URI(uri)
        self.attributes['uri'] = uri

    def get(self, key, default=None):
        """Get an attribute, but if it doesn't exist return a default value."""
        return self.attributes.get(key, default)

    def excerpt(self, terms, max_len=240, fuzz=60):
        """Generate an Excerpt from this Hit."""
        try:
            current = True
            doc = self.current
        except:
            current = False
            doc = self.indexed
        return Excerpt(doc, terms, max_len, fuzz, current)

    def __getattr__(self, key):
        """Access hit attributes."""
        try:
            return self.attributes[key]
        except KeyError, e:
            raise AttributeError(unicode(e))

    def __contains__(self, key):
        """Determine whether a Hit contains an attribute."""
        return key in self.attributes

    def __repr__(self):
        return '<Hit %s>' % ' '.join(['%s=%s' % (k, repr(v)) for k, v in
                                              self.attributes.iteritems()])

    def _get_current(self):
        """Fetch current Document (if possible)."""
        if callable(self._current):
            self._current = self._current(self.uri)
        return self._current
    current = property(_get_current)

    def _get_indexed(self):
        """Fetch Indexer representation of Document (if possible)."""
        if callable(self._indexed):
            self._indexed = self._indexed(self.uri)
        return self._indexed
    indexed = property(_get_indexed)


class Excerpt(object):
    """Generate an excerpt of a Document.

    Has three useful attributes:

    ``current``
        Whether this is a current copy of the `Document` (as opposed to a
        historical version from the `Indexer`)

    ``quality``
        Quality of the text compared to the original, between 0.0 and 1.0.

    ``text``
        The excerpt text.

    """
    def __init__(self, doc, terms, max_len=240, fuzz=60, current=True):
        self.text = self._shorten(doc.content, terms, max_len, fuzz)
        self.quality = doc.quality
        self.current = current

    def _shorten(self, text, terms, max_len=240, fuzz=60):
        # FIXME Take into account stemming
        # FIXME Take into account whole-word only search, or
        # wild-card...etc.??? Tricky.
        text_low = text.lower()
        beg = -1
        for k in terms:
            i = text_low.find(k.lower())
            if (i > -1 and i < beg) or beg == -1:
                beg = i
        excerpt_beg = 0
        if beg > fuzz:
            for sep in ('.', ':', ';', '='):
                eb = text.find(sep, beg - fuzz, beg - 1)
                if eb > -1:
                    eb += 1
                    break
            else:
                eb = beg - fuzz
            excerpt_beg = eb
        if excerpt_beg < 0:
            excerpt_beg = 0
        msg = text[excerpt_beg:beg+max_len]
        if beg > fuzz:
            msg = '... ' + msg
        if beg < len(text)-max_len:
            msg = msg + ' ...'
        return msg

    def __repr__(self):
        return self.text
