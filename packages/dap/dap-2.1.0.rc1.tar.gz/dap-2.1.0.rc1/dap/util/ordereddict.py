"""Ordered dictionary.

This is a dictionary class that preserves the order in which the keys are
stored. This is necessary to build Structures and Sequences that follow the
requested variable order.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

class odict(object):
    """Ordered dictionary.

    This is a normal dictionary:

        >>> undict = {}
        >>> undict[1] = 1
        >>> undict[0] = 2
        >>> undict[1.1] = 3
        >>> undict['a'] = 4
        >>> undict.values()
        [2, 1, 4, 3]
        >>> for i in undict:
        ...    print i
        0
        1
        a
        1.1

    Note that key insertion order is not preserved (for speed). Now with
    an ordered dictionary:

        >>> ordict = odict()
        >>> ordict[1] = 1
        >>> ordict[0] = 2
        >>> ordict[1.1] = 3
        >>> ordict['a'] = 4
        >>> ordict.values()
        [1, 2, 3, 4]
        >>> for i in ordict:
        ...     print i
        1
        0
        1.1
        a
    """
    def __init__(self, dict=None):
        self._keys = []
        self._dict = {}

        if dict is not None:
            self.update(dict)

    def __repr__(self):
        return repr(self._dict)
            
    def __setitem__(self, key, item):
        self._dict.__setitem__(key, item)
        if key not in self._keys: self._keys.append(key)

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __delitem__(self, key):
        self._dict.__delitem__(key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys[:])

    def clear(self):
        self._dict.clear()
        self._keys = []

    def copy(self):
        new = odict(self._dict)
        return new

    def items(self):
        return zip(self._keys, map(self._dict.get, self._keys))

    def keys(self):
        return self._keys[:]

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        self._keys.remove(key)
        return self._dict.popitem()
        
    def setdefault(self, key, failobj=None):
        if key not in self._keys: self._keys.append(key)
        return self._dict.setdefault(key, failobj)

    def update(self, dict):
        for (key,val) in dict.items():
            self.__setitem__(key, val)

    def values(self):
        return map(self._dict.get, self._keys)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
