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
from pocoo.template import FileRequirements


class CobaltMiddleware(object):
    """
    The Cobalt middleware serves static files.
    """

    def __init__(self, app, ctx):
        self.app = app
        self.ctx = ctx
        self.cache_enabled = ctx.cfg.get_bool('cache', 'static_cache')

    def get_stylesheet_imports(self):
        if not self.cache_enabled or 'cobalt/stylesheet_imports' not in self.ctx._cache:
            handled = set()
            lines = []
            for comp in self.ctx.get_components(FileRequirements):
                for name in comp.get_stylesheet_imports():
                    item = (comp.package, name)
                    if item in handled:
                        continue
                    handled.add(item)
                    if item[1].startswith('/'):
                        url = self.ctx.make_url(item[1][1:])
                    else:
                        url = '!cobalt/%s/%s' % item
                    lines.append('@import url(%s);' % str(self.ctx.make_url(url)))
            self.ctx._cache['cobalt/stylesheet_imports'] = '\n'.join(lines)
        return self.ctx._cache['cobalt/stylesheet_imports']

    def get_javascript_imports(self):
        if not self.cache_enabled or 'cobalt/javascript_imports' not in self.ctx._cache:
            handled = set()
            lines = []
            onload = []
            for comp in self.ctx.get_components(FileRequirements):
                for name in comp.get_javascript_imports():
                    item = (comp.package, name)
                    if item in handled:
                        continue
                    handled.add(item)
                    imp = self.ctx.pkgmanager.importers[comp.package]
                    lines.append(imp.get_data(os.path.join('static', name)))
            self.ctx._cache['cobalt/javascript_imports'] = '\n\n'.join(lines)
        return self.ctx._cache['cobalt/javascript_imports']

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        if path.startswith('/!cobalt/'):
            mime_type = None
            try:
                pkgname, fname = path[9:].split('/', 1)
                if pkgname == '_import_':
                    if fname == 'styles.css':
                        mime_type = 'text/css'
                        content = self.get_stylesheet_imports()
                    elif fname == 'script.js':
                        mime_type = 'application/x-javascript'
                        content = self.get_javascript_imports()
                else:
                    guessed_type = guess_type(fname)
                    mime_type = guessed_type[0] or 'text/plain'
                    imp = self.ctx.pkgmanager.importers[pkgname]
                    content = imp.get_data(os.path.join('static', fname))
                if mime_type is not None:
                    expiry = time.time() + 3600   # cache for one hour
                    expiry = time.asctime(time.gmtime(expiry))
                    headers = [('Content-Type', mime_type),
                               ('Cache-Control', 'public'),
                               ('Expires', expiry)]
                    start_response('200 OK', headers)
                    if environ.get('REQUEST_METHOD', 'GET') == 'HEAD':
                        return []
                    else:
                        return [content]
            except (ValueError, KeyError, IOError):
                # XXX: output custom error message?
                pass
        return self.app(environ, start_response)
