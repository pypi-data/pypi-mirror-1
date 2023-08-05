# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.cache
    ~~~~~~~~~~~~~~~~~~~~

    Provides a very simple caching system for persistent processes.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.application import RequestWrapper
from pocoo.exceptions import PocooRuntimeError
from pocoo.utils.cache import Cache

# This is currently unused.

class CacheSystem(RequestWrapper):

    def __init__(self, ctx):
        self.cache = Cache(autoprune=ctx.cfg.get('cache', 'autoprune', False))
        self.uri2key = {}
        RequestWrapper.__init__(self, ctx)

    def get_priority(self):
        # caching has highest priority
        return 1

    def process_request(self, req):
        req.cache_control = None
        req.cache = self.cache

        if req.environ['REQUEST_METHOD'] != 'GET':
            return
        if req.environ['REQUEST_URI'] not in self.uri2key:
            return

        key = self.uri2key[req.environ['REQUEST_URI']]
        return self.cache.fetch(key, None)

    def process_response(self, req, resp):
        if not req.cache_control:
            return resp

        action, key = req.cache_control
        if action == 'set':
            self.cache.dump(key, resp)
            self.uri2key[req.environ['REQUEST_URI']] = key
        elif action == 'update':
            if isinstance(key, basestring):
                self.cache.remove(key)
            else:
                for k in key:
                    self.cache.remove(k)
        else:
            raise PocooRuntimeError('req.cache_control invalid')

        return resp
