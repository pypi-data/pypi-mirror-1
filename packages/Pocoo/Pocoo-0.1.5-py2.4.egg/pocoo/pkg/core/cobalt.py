# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.cobalt
    ~~~~~~~~~~~~~~~~~~~~~

    Provides static content serving like mozilla's chrome:// scheme.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import os
import time
from mimetypes import guess_type


class CobaltMiddleware(object):
    """
    The Cobalt middleware serves static files.
    """

    def __init__(self, app, ctx):
        self.app = app
        self.ctx = ctx

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        if path.startswith('/!cobalt/'):
            try:
                pkgname, fname = path[9:].split('/', 1)
                guessed_type = guess_type(fname)
                mime_type = guessed_type[0] or 'text/plain'
                imp = self.ctx.pkgmanager.importers[pkgname]
                result = imp.get_data(os.path.join('static', fname))

                expiry = time.time() + 3600   # cache for one hour
                expiry = time.asctime(time.gmtime(expiry))
                headers = [('Content-Type', mime_type),
                           ('Cache-Control', 'public'),
                           ('Expires', expiry)]
                start_response('200 OK', headers)
                if environ.get('REQUEST_METHOD', 'GET') == 'HEAD':
                    return []
                else:
                    return iter((result,))
            except (ValueError, KeyError, IOError):
                # XXX: output custom error message?
                pass
        return self.app(environ, start_response)
