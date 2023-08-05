from pyndexter import *
from urlparse import urlsplit
import pickle

class MetaSource(Source):
    """ A collection of sources. If sources serve the same documents the
    results will be undefined, and probably not good. """
    def __init__(self, sources=None):
        self.sources = sources or []

    def add_source(self, source):
        """ Add an additional source to the collection. """
        self.sources.append(source)

    def __hash__(self):
        raise SourceError('MetaSource can not be hashed')

    def __iter__(self):
        for source in self.sources:
            for uri in source:
                yield uri

    def matches(self, uri):
        for source in self.sources:
            if source.matches(uri):
                return True
        return False

    def fetch(self, uri):
        for source in self.sources:
            if source.matches(uri):
                return source.fetch(uri)
        raise DocumentNotFound(uri)

    def exists(self, uri):
        for source in self.sources:
            if source.exists(uri):
                return True
        return False

    def state(self):
        state = {}
        for source in self.sources:
            state[hash(source)] = source.state()
        return pickle.dumps(state, 2)

    def difference(self, state):
        try:
            state = pickle.loads(state)
        except Exception, e:
            raise InvalidState('Invalid state provided to MetaSource. '
                               'Exception was %s: %s' % (e.__class__.__name__, e))
        for source in self.sources:
            if hash(source) not in state:
                for uri in source:
                    yield (ADDED, uri)
            else:
                for change in source.difference(state[hash(source)]):
                    yield change
