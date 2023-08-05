# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.remotecall
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Pocoo remote call support.


    Remote Call Implementation
    ==========================

    The Pocoo XMLRPC/JSONRPC interface works like this::

        import time
        from pocoo.pkg.core.remotecall import RemoteCallable, export

        class MyClass(RemoteCallable):

            @export("test.hello_world")
            def say(self, req, name='World'):
                return 'Hello %s!' % name

            @export("test.get_servertime")
            def servertime(self, req):
                return time.time()

    By now only jsonrpc is available. You can query the jsonrpc interface
    under ``/!jsonrpc``. The exported names are ``packagename.<name>``.
    So for the example above the method names are (assumed that the module
    is in package ``core``)::

        core.test.hello_world

    and::

        core.test.get_servertime


    JavaScript Query
    =================

    You can query those functions using the following syntax::

        var rpc = new pocoo.lib.async.RPC('!jsonrpc');
        var method = rpc.getMethod('methodname');
        method(arguments, kwarguments, callback);

    The query for the example above would be::

        var rpc = new pocoo.lib.async.RPC('!jsonrpc');
        var method = rpc.getMethod('core.test.hello_world');
        method(["Benjamin"], {}, function (result) {
            alert(result);
            // alerts "Hello Benjamin!"
        });


    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import new
from types import FunctionType
from pocoo.http import DirectResponse
from pocoo.context import Component
from pocoo.application import RequestHandler
from pocoo.http import Response
from pocoo.utils import json


class _RemoteCallableMeta(type):

    def __new__(cls, name, bases, d):
        rpc_exports = {}
        result = type.__new__(cls, name, bases, d)
        for name, ref in d.iteritems():
            if isinstance(ref, FunctionType) and \
               getattr(ref, 'rpc_exported', False):
                name = '%s.%s' % (ref.__module__.split('.')[2],
                                  ref.rpc_name)
                rpc_exports[name] = ref
        result.rpc_exports = rpc_exports
        return result


class RemoteCallable(Component):
    """
    Components inheriting from this base component can export methods
    for jsonrpc if they are decorated using `export`.

    Example::

        from pocoo.pkg.core.remotecall import RemoteCallable, export

        class MyExport(RemoteCallable):
    """
    __metaclass__ = _RemoteCallableMeta


class RemoteCallManager(RequestHandler):

    handler_regexes = [r'!jsonrpc$']

    def __init__(self, ctx):
        super(RemoteCallManager, self).__init__(ctx)
        self._mapping = None

    def handle_request(self, req):
        # TODO: once jsonrpc1.1 is finished: update error codes
        if self._mapping is None:
            self._mapping = {}
            for comp in self.ctx.get_components(RemoteCallable):
                for name, ref in comp.rpc_exports.iteritems():
                    handler = new.instancemethod(ref, comp, comp.__class__)
                    self._mapping[name] = handler
        id = None
        try:
            method, args, kwargs, id = json.parse_jsonrpc_request(req.data)
            handler = self._mapping[method]
            json_data = {
                'version':  '1.1',
                'result':   handler(req, *args, **kwargs)
            }
            if id is not None:
                json_data['id'] = id
        except DirectResponse, e:
            return e.args[0]
        except Exception, e:
            error = {
                'msg':      str(e),
                'type':     e.__class__.__name__
            }
            for name, ref in e.__dict__.iteritems():
                if not name.startswith('_') and\
                   isinstance(ref, (str, unicode, int, float, tuple,
                              list, dict)):
                    error[name] = ref
            json_data = {
                'version':  '1.1',
                'error': {
                    'name':     'JSONRPCError',
                    'code':     000,
                    'message':  'An error occurred parsing the request object.',
                    'error':    error
                }
            }
            if id is not None:
                json_data['id'] = id
        return Response(json.dumps(json_data),
                        [('Content-Type', 'text/javascript')])


def export(name):
    """
    Exports a function in a RemoteCallable component.
    """
    def wrapped(f):
        f.rpc_exported = True
        f.rpc_name = name
        return f
    return wrapped
