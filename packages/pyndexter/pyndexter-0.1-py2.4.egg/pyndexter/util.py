import time
from UserDict import DictMixin
try:
    set = set
except:
    from sets import Set as set

class CacheDict(DictMixin):
    """ A caching dictionary, with a bounded size. """
    def __init__(self, size):
        self.size = size
        self.data = {}
        self.accessbykey = {}
        self.accessbytime = {}

    def __setitem__(self, key, value):
        self.data[key] = value
        self._update_cache(key)

    def __getitem__(self, key):
        value = self.data[key]
        self._update_cache(key)
        return value

    def __delitem__(self, key):
        age = self.accessbykey[key]
        del self.accessbytime[age]
        del self.accessbykey[key]
        del self.data[key]

    def keys(self):
        return self.data.keys()

    # Internal methods
    def _update_cache(self, key):
        t = time.time()
        if key in self.accessbykey:
            del self.accessbytime[self.accessbykey[key]]
        self.accessbykey[key] = t
        self.accessbytime[t] = key
        if len(self.accessbykey) >= self.size:
            oldest = self.accessbytime.keys()
            oldest.sort()
            oldest = oldest[:self.size / 2]
            for age in oldest:
                key = self.accessbytime[age]
                del self[key]
