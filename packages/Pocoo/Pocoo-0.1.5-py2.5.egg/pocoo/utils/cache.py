# -*- coding: utf-8 -*-
"""
    pocoo.utils.cache
    ~~~~~~~~~~~~~~~~~

    Provides a very simple caching system for persistent processes.

    **This is currently unused and untested.**

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import copy
import time

from pocoo.exceptions import PocooRuntimeError


class Cache(object):
    """
    A simple memory caching system.

    Usage example::

        >>> from pocoo.utils.cache import Cache
        >>> memcache = Cache()
        >>> memcache.dump('test', 'Hello World', 5)
        >>> memcache.fetch('test')
        'Hello World'
        >>> memcache.fetch('test')
        'Hello World'
        >>> memcache.fetch('test')
        'Hello World'
        >>> memcache.fetch('test')
        >>> memcache.expired('test')
        True
        >>> memcache['blub'] = 'Test'
        >>> memcache['blub']
        'Test'
        >>> memcache['blub', 2] = 'Spam'
        >>> memcache['blub']
        'Spam'
        >>> memcache.expired('blub')
        True
    """

    def __init__(self, autoprune):
        self._cache = {}
        self.autoprune = autoprune

    def __repr__(self):
        d = {}
        for key in self._cache:
            if not self.expired(key):
                d[key] = self.fetch(key)
        return '<Cache %r - caching %d items, %d expired>' % (
            d, len(d), len(self._cache) - len(d))

    def dump(self, key, obj, expires=360):
        if expires > -1:
            expires = time.time() + expires
        self._cache[key] = (copy.copy(obj), expires)

    def fetch(self, key, default=None):
        if self.autoprune:
            self.prune()
        if not self.expired(key):
            return self._cache[key][0]
        return default

    def remove(self, key):
        if key in self._cache:
            del self._cache[key]

    def prune(self):
        ncache = {}
        for key in self._cache:
            if not self.expired(key):
                ncache[key] = self._cache[key]
        self._cache = ncache

    def expired(self, key):
        if key not in self._cache:
            return True
        if self._cache[key][1] < 0:
            return False
        return self._cache[key][1] < time.time()

    def new(self, key):
        return key not in self._cache

    def __contains__(self, key):
        return not self.expired(key)

    def __getitem__(self, item):
        return self.fetch(item)

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            key, expires = item
        elif isinstance(item, str):
            key = item
            expires = -1
        else:
            raise PocooRuntimeError('string expected')
        self.dump(key, value, expires)
