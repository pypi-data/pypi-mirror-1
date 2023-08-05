# -*- coding: utf-8 -*-
"""
    pocoo.utils.tests
    ~~~~~~~~~~~~~~~~~

    Unittest utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from cStringIO import StringIO
from urlparse import urlparse
from pocoo.utils.net import IP
from pocoo.utils.uri import urlencode


# positions
UNINITIALIZED = 'uninitialized'
SERVER_INIT = 'server_init'
APPLICATION_INIT = 'application_init'
START_OUTPUT = 'start_output'
OUTPUT = 'output'
END_OUTPUT = 'end_output'
CLOSING_APPLICATION = 'closing_application'
SKIP_APPLICATION_CLOSE = 'skip_application_close'



class InteractivePocoo(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def get(self, **kwargs):
        controller = self.partial_response(**kwargs)
        controller.run()
        return controller

    def partial_response(self, **kwargs):
        srv = BufferedServer(self.ctx)
        return srv.start_response(**kwargs)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.ctx
        )


class BufferedServer(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def start_response(self, url='/', params=None, query_string='',
                       cookie='', remote_addr='127.0.0.1',
                       request_method='POST', input_stream=None):
        # server environment
        if input_stream is None:
            input_stream = StringIO('')
        error_stream = StringIO()
        if params and not query_string:
            query_string = urlencode(params)

        scheme, host = urlparse(str(self.ctx.serverpath))[:2]
        if ':' in host:
            servername, serverport = host.split(':', 1)
        else:
            servername = host
            serverport = '80'

        environ = {
            'wsgi.input':           input_stream,
            'wsgi.errors':          error_stream,
            'wsgi.version':         (1, 0),
            'wsgi.multithread':     False,
            'wsgi.multiprocess':    True,
            'wsgi.run_once':        False,
            'wsgi.url_scheme':      scheme,
            'QUERY_STRING':         query_string,
            'SCRIPT_NAME':          str(self.ctx.scriptname),
            'PATH_INFO':            url,
            'HTTP_COOKIE':          cookie,
            'HTTP_HOST':            host,
            'SERVER_NAME':          servername,
            'SERVER_PORT':          serverport,
            'SERVER_ADDR':          str(IP.by_hostname(servername)),
            'REMOTE_ADDR':          remote_addr,
            'REQUEST_METHOD':       request_method
        }

        stream = StringIO()
        _headers_set = []
        _headers_sent = []

        def write(data):
            if not _headers_set:
                raise AssertionError("write() before start_response()")

            elif not _headers_sent:
                # Before the first output, send the stored headers
                status, response_headers = _headers_sent[:] = _headers_set
                try:
                    controller.status = status
                    controller.headers = response_headers
                except NameError:
                    pass
                stream.write('Status: %s\r\n' % status)
                for header in response_headers:
                    stream.write('%s: %s\r\n' % header)
                stream.write('\r\n')

            stream.write(data)
            if hasattr(stream, 'flush'):
                stream.flush()

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if _headers_sent:
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None
            elif _headers_set:
                raise AssertionError('Headers already set!')
            _headers_set[:] = (status, response_headers)
            return write

        def proxy():
            yield SERVER_INIT
            app = self.ctx(environ, start_response)
            yield APPLICATION_INIT
            appiter = iter(app)
            yield START_OUTPUT
            for line in appiter:
                write(line)
                yield OUTPUT
            yield END_OUTPUT
            if hasattr(appiter, 'close'):
                yield CLOSING_APPLICATION
                appiter.close()
            else:
                yield SKIP_APPLICATION_CLOSE
        controller = InteractiveController(self.ctx, stream, environ, proxy())
        return controller


class ApplicationClosed(Exception):
    pass


class InteractiveController(object):

    def __init__(self, ctx, stream, environ, iterable):
        self.ctx = ctx
        self.output_stream = stream
        self.input_stream = environ['wsgi.input']
        self.error_stream = environ['wsgi.errors']
        self.environ = environ
        self.headers = []
        self.status = '000 UNKNOWN'
        self._iterable = iterable
        self._stack = []

    @property
    def body(self):
        return self.output_stream.getvalue()

    @property
    def position(self):
        if not self._stack:
            return UNINITIALIZED
        else:
            return self._stack[-1]

    @property
    def req(self):
        return self.environ['colubrid.request']

    def run(self):
        try:
            while True:
                self.step()
        except ApplicationClosed:
            return

    def run_until(self, needle):
        try:
            while True:
                if self.step() == needle:
                    return
        except ApplicationClosed:
            return

    def step(self):
        try:
            d = self._iterable.next()
            self._stack.append(d)
        except StopIteration:
            raise ApplicationClosed()
        return d

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.position
        )


class UnboundRequest(object):

    def __init__(self, controller):
        self.__dict__['controller'] = controller
        self.__dict__['alive'] = True

    def __getattr__(self, attr):
        if attr == '__members__':
            return dir(self.controller.req)
        return getattr(self.controller.req, attr)

    def __setattr__(self, attr, value):
        if hasattr(self.controller.req, attr):
            setattr(self.controller.req, attr, value)
        else:
            self.__dict__[attr] = value

    def shutdown(self):
        if self.alive:
            self.controller.run()
            self.__dict__['alive'] = False

    def __repr__(self):
        return '<%s %r%s>' % (
            self.__class__.__name__,
            self.controller.req.path,
            self.alive and ' *' or ''
        )


def get_unbound_request(ctx, **kwargs):
    ipocoo = InteractivePocoo(ctx)
    c = ipocoo.partial_response(**kwargs)
    c.run_until(OUTPUT)
    return UnboundRequest(c)
