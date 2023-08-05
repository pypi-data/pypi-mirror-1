# -*- coding: utf-8 -*-
"""
    pocoo.utils.collections
    ~~~~~~~~~~~~~~~~~~~~~~~

    Collection utilities.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747,
# with some modifications

class OrderedDict(dict):
    def __init__(self, __dct__=None, **items):
        if __dct__:
            dict.__init__(self, __dct__)
        else:
            dict.__init__(self, **items)
        self._keys = dict.keys(self)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        dict.clear(self)
        self._keys = []

    def copy(self):
        dct = self.__class__(self)
        dct._keys = self._keys[:]
        return dct

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        dict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dct):
        dict.update(self, dct)
        for key in dct.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)


class CallbackDict(dict):
    """
    A dictionary that calls an arbitrary function on
    setting and deleting values.
    """

    def __init__(self, _callback_, **kwds):
        dict.__init__(self, **kwds)
        self._cb = _callback_

    def clear(self):
        for key in self:
            self._cb(self, key, None)
        super(CallbackDict, self).clear()

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).iteritems():
            self._cb(self, key, value)
            self[key] = value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self._cb(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._cb(self, key, None)


class AttrDict(dict):
    """
    A dictionary for which attribute access is equivalent
    to item access.
    """

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


def dict_diff(d1, d2):
    """
    Return the difference of dictionaries ``d1`` and ``d2``::

        >>> d1 = {"foo": "bar", "spam": "eggs"}
        >>> d2 = {"foo": "bar", "spam": "EGGS"}
        >>> dict_diff(d1, d2)
        {'spam': 'EGGS'}
    """
    set1 = set(d1.items())
    set2 = set(d2.items())
    diff = set2 - set1.intersection(set2)
    return dict(diff)
