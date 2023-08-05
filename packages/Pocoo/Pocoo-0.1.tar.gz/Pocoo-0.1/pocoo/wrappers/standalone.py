# -*- coding: utf-8 -*-
"""
    pocoo.wrappers.standalone
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    A basic WSGI server implementation, for running the
    Pocoo development server.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
import socket

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse


class WSGIRequestHandler(BaseHTTPRequestHandler):

    def run_wsgi(self):
        path_info, _, query = urlparse(self.path)[2:5]
        app = self.server.application
        environ = {
            'wsgi.version':         (1,0),
            'wsgi.url_scheme':      'http',
            'wsgi.input':           self.rfile,
            'wsgi.errors':          sys.stderr,
            'wsgi.multithread':     1,
            'wsgi.multiprocess':    0,
            'wsgi.run_once':        0,
            'REQUEST_METHOD':       self.command,
            'SCRIPT_NAME':          '',
            'QUERY_STRING':         query,
            'CONTENT_TYPE':         self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH':       self.headers.get('Content-Length', ''),
            'REMOTE_ADDR':          self.client_address[0],
            'REMOTE_PORT':          self.client_address[1],
            'SERVER_NAME':          self.server.server_address[0],
            'SERVER_PORT':          str(self.server.server_address[1]),
            'SERVER_PROTOCOL':      self.request_version
        }
        if path_info:
            from urllib import unquote
            environ['PATH_INFO'] = unquote(path_info)
        for key, value in self.headers.items():
            environ['HTTP_' + key.upper().replace('-', '_')] = value

        headers_set = []
        headers_sent = []

        def write(data):
            if not headers_set:
                raise AssertionError('write() before start_response')
            elif not headers_sent:
                status, response_headers = headers_sent[:] = headers_set
                code, msg = status.split(' ', 1)
                self.send_response(int(code), msg)
                for line in response_headers:
                    self.send_header(*line)
                self.end_headers()

            if type(data) is not str:
                raise AssertionError('wsgi application must write \'str\' objects.')
            self.wfile.write(data)

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None
            elif headers_set:
                raise AssertionError('Headers already set.')
            headers_set[:] = [status, response_headers]
            return write

        try:
            application_iter = app(environ, start_response)
            try:
                for data in application_iter:
                    write(data)
            finally:
                if hasattr(application_iter, 'close'):
                    application_iter.close()
        except (socket.error, socket.timeout):
            return
        except:
            exc_info = sys.exc_info()
            try:
                start_response('500 INTERNAL SERVER ERROR' ,
                               [('Content-type', 'text/plain')])
            except AssertionError:
                pass
            import traceback
            write(''.join(traceback.format_exception(*exc_info)))


    do_POST = do_HEAD = do_HEAD = do_DELETE = do_PUT = \
              do_TRACE = do_GET = run_wsgi


class WSGIServer(ThreadingMixIn, HTTPServer):

    def __init__(self, application, hostname='localhost', port=8080):
        HTTPServer.__init__(self, (hostname, int(port)), WSGIRequestHandler)
        self.application = application

    def serve_forever(self):
        try:
            HTTPServer.serve_forever(self)
        except KeyboardInterrupt:
            pass
