# -*- coding: utf-8 -*-
"""
    pocoo.pkg.latex
    ~~~~~~~~~~~~~~~

    Pocoo package supporting LaTeX markup.

    This package needs the **latex** and **dvipng** shell commands
    to work properly.

    For latex, any recent LaTeX distribution should suffice,
    dvipng can be obtained from http://dvipng.sourceforge.net/.

    The ``LatexRender`` class in render.py renders a piece of LaTeX
    math mode markup to a PNG graphics file and stores it in the
    instance folder under latex/ using the SHA1 hash of the
    markup.
    Some potentially harmful LaTeX commands (like \input) are detected
    and the string is rejected if found. Also, it cannot have a length
    of more than 1000 characters.

    The `LatexMiddleware` allows remote access to these images
    via the /!latex/ virtual directory.

    The `LatexBBCodeTagProvider` class provides a BBCode tag
    ``[math]`` to start that machinery. On error, the markup
    is output as plain text with an error

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import os, time

from pocoo.utils.html import unescape_html, escape_html
from pocoo.pkg.core.bbcode import BBCodeTagProvider
from pocoo.pkg.latex.render import LatexRender

# TODO: help page?


class LatexMiddleware(object):
    """
    The LaTeX middleware handles !latex/ requests.
    """

    def __init__(self, app, ctx):
        self.app = app
        self.ctx = ctx
        self.latexpath = os.path.join(ctx.cfg.root, 'latex')

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        if path.startswith('/!latex/'):
            try:
                fn = path[8:]
                content = file(os.path.join(self.latexpath, fn), 'rb').read()
                expiry = time.time() + 3600   # cache for one hour
                expiry = time.asctime(time.gmtime(expiry))
                headers = [('Content-Type', 'image/png'),
                           ('Cache-Control', 'public'),
                           ('Expires', expiry)]
                start_response('200 OK', headers)
                if environ.get('REQUEST_METHOD', 'GET') == 'HEAD':
                    return []
                else:
                    return [content]
            except IOError:
                # the 404 is rendered by the application
                pass
        return self.app(environ, start_response)


class LatexBBCodeTagProvider(BBCodeTagProvider):
    """
    Render ``[math]latex code[/math]`` tags.
    """

    def __init__(self, ctx):
        self.renderer = LatexRender(os.path.join(ctx.cfg.root, 'latex'))
        super(LatexBBCodeTagProvider, self).__init__(ctx)

    def get_node(self, token, parser):
        if token.name == 'math':
            latex = parser.get_tokens('/math').flatten()
            fn, err = self.renderer.render(unescape_html(latex))
            if not fn:
                return '[LaTeX: %s (%s)]' % (latex, err)
            url = self.ctx.make_url('!latex/' + fn)
            return '<img style="margin: 10px" src="%s" alt="%s"/>' % (url, latex)
