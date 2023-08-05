# -*- coding: utf-8 -*-
"""
    pocoo.application
    ~~~~~~~~~~~~~~~~~

    Pocoo WSGI application and base component types.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
import time
import urllib

from pocoo import Component
from pocoo.http import Request, Response, DirectResponse, \
     PageNotFound, PageMoved
from pocoo.utils.debug import dtk


class RequestHandler(Component):
    """
    Component for URL <-> handler mapping.

    For each request, `Pocoo.__call__` loops through the
    `handler_regexes` of all registered `RequestHandler` components
    and calls `handle_request` on the first match.
    """

    #: Iterable of regexes which match the relative url of this page.
    handler_regexes = None

    def handle_request(self, req, *args):
        """
        Called if the current request path matches one of the
        `handler_regexes`.

        In all normal cases this must return a `pocoo.http.Response`
        (or a subclass thereof) or raise `pocoo.http.DirectResponse`.
        It can also return ``None`` to signal "page not found".
        """


class RequestWrapper(Component):
    """
    RequestWrappers process the request before it is given
    to the RequestHandler and process the response before
    it is given back to Colubrid.
    """

    def process_request(self, req):
        """
        Process the request.

        Can return a Response to bypass further request handling
        (especially any `pocoo.application.RequestHandler` components),
        else ``None``.
        """

    def process_response(self, req, resp):
        """
        Process the response.

        Must return the same or a new response object.
        """

    def get_priority(self):
        """
        Return an integer priority that indicates when the RequestWrapper
        should be applied:

        1
          before all others on request, after all others on response
        100
          after all others on request, before all others on response

        Levels 1 to 10 are reserved for pocoo core.
        """


class LinkableMixin(object):
    """
    Provides support for easy link creation.
    """
    relative_url = ''

    @property
    def external_url(self):
        return '%s%s%s' % (
            self.ctx.servername,
            self.ctx.scriptname,
            self.relative_url
        )

    @property
    def url(self):
        return '%s%s' % (self.ctx.scriptname, self.relative_url)


class Pocoo(object):
    """
    The main Pocoo WSGI application.
    """

    url_wrappers = None
    url_mapping = None

    def __init__(self, ctx):
        """
        Setup the application.

        This is done after all components are registered, so we can already
        collect the RequestHandlers here.
        """
        self.ctx = ctx

        mapping = {}
        for comp in ctx.get_components(RequestHandler):
            for regex in comp.handler_regexes:
                if not isinstance(regex, basestring):
                    regex, args = regex
                else:
                    args = {}
                mapping[re.compile(regex), regex] = (comp, args)
        self.url_mapping = mapping
        self.url_wrappers = ctx.get_components(RequestWrapper)
        self.url_wrappers.sort(key=lambda wr: (wr.get_priority() or 100))

    def __call__(self, environ, start_response):
        """
        The main request dispatching machinery.

        This tries to call `RequestHandler.handle_request` on the first
        RequestHandler for which one of the handler regexes matches the
        relative part of the request URL.
        Additionally, it calls the ``process_request`` and ``process_response``
        methods of `RequestWrapper` components in the right order.
        If it doesn't find a handler, a 404 response is returned.
        """
        req = Request(environ, start_response, self.ctx)
        # copy request into environ to allow DebuggedApplication
        # query the request attributes
        environ['colubrid.request'] = req

        t_1 = time.time()

        # ignore any stupid favicon.ico lookups
        # we check this before any regex check to improve
        # performance. Because of this it's impossible to
        # create a regex like favicon.ico$ which matches since
        # it could never reach that check
        if req.path.split('/')[-1] == 'favicon.ico':
            return Response(u'', status=404)(req)

        # process request wrappers
        for wrapper in self.url_wrappers:
            ret = wrapper.process_request(req)
            if isinstance(ret, Response):
                return ret(req)

        # check if we have a leading slash
        if not req.environ.get('PATH_INFO', '').startswith('/'):
            resp = PageMoved('')
        else:
            try:
                for (r, _), (handler, default) in self.url_mapping.iteritems():
                    m = r.match(req.path)
                    if m is None:
                        continue
                    args = m.groupdict()
                    args.update(default)
                    resp = handler.handle_request(req, **args)
                    if resp is None:
                        resp = PageNotFound()
                    break
                else:
                    resp = PageNotFound()
            except DirectResponse, exc:
                resp = exc.args[0]

            # Handle special error404 cases (automatic redirects for
            # trailing slashes or favicon lookups)
            if resp.status == 404 and not req.path.endswith('/'):
                # Now let's check if the request might be successful
                # if the user would access the page with a trailing '/'
                test = req.path + '/'
                for (regex, _), _ in self.url_mapping.iteritems():
                    if regex.match(test) is not None:
                        # the regex test proves that the url with a
                        # trailing slash has a handler so create
                        # a redirect
                        url = ''.join([
                            urllib.quote(environ.get('SCRIPT_NAME', '')),
                            urllib.quote(environ.get('PATH_INFO', ''))
                        ])
                        query = environ.get('QUERY_STRING', '')
                        if query:
                            url = '%s/?%s' % (url, query)
                        else:
                            url += '/'
                        resp = PageMoved(url)
                        break

        for wrapper in reversed(self.url_wrappers):
            resp = wrapper.process_response(req, resp)

        t_2 = time.time()
        dtk.log('app', 'handled request to %r in %0.5f sec', req.path, t_2 - t_1)

        return resp(req)


def setup_app(ctx):
    """
    Create the application object, wrap it in the requested debug middleware
    and return it to the context.

    Also wrap the application in all middlewares registered to the context
    via ``register_middleware`` or ``package.conf`` files.
    """
    app = Pocoo(ctx)
    debug = ctx.cfg.get_bool('development', 'debug', False)
    evalex = debug and ctx.cfg.get_bool('development', 'enable_evalexception', False)
    if debug:
        from colubrid.debug import DebuggedApplication
        app = DebuggedApplication(app, evalex)
    else:
        # TODO: add an error catching middleware that renders and
        #       500 INTERNAL SERVER ERROR page based upon the
        #       error_500.html template and which sends mails to
        #       the admins in the list if wanted
        #       (perhaps add it to Pocoo.__call__)
        pass
    # Apply package supplied middlewares
    for mware in ctx.middlewares:
        app = mware(app, ctx)
    return app
