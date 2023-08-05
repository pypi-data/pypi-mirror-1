# -*- coding: utf-8 -*-
"""
    pocoo.utils.collections
    ~~~~~~~~~~~~~~~~~~~~~~~

    Collection utilities.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

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
