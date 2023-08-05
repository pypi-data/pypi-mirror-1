# -*- coding: utf-8 -*-
"""
    pocoo.utils.json
    ~~~~~~~~~~~~~~~~

    This file does not directly provide JSON dumping/parsing methods
    but imports the required methods from various JSON parsers.

    Currently supported:

    * simplejson: http://undefined.org/python/#simple_json
    * python-json: http://cheeseshop.python.org/pypi/python-json

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from datetime import datetime, tzinfo
from pocoo.exceptions import PocooRuntimeError

__all__ = ['dump', 'load', 'dumps', 'loads', 'parse_jsonrpc_request',
           'dump_datetime', 'parse_datetime']

try:
    # pylint: disable-msg=W0611
    from simplejson import dump, load, dumps, loads

except ImportError:
    try:
        _json = __import__('json')
        _ = _json.JsonReader, _json.JsonWriter
    except (ImportError, AttributeError):
        raise PocooRuntimeError("No supported JSON library is installed! "
                                "Please install either simplejson "
                                "or python-json.")

    def dump(obj, fileobj):
        """Serialize ``obj`` to the file object ``fileobj``."""
        fileobj.write(_json.write(obj))

    def load(fileobj):
        """Load serialized data form the file object ``fileobj``."""
        return _json.read(fileobj.read())

    def dumps(obj):
        """Return ``obj`` serialized as a string."""
        return _json.write(obj)

    def loads(s):
        """Load serialized data from the string ``s``."""
        return _json.read(s)


def parse_jsonrpc_request(data):
    """
    Give the method a string and it will return all information required
    so that you can call an exported method according to jsonrpc 1.1

    :return: (method, args, kwargs, id)
    """
    try:
        request = loads(data)
    except:
        raise ValueError('malformed json')
    if not isinstance(request, dict):
        raise ValueError('invalid request')
    if float(request.get('version', '1.0')) < 1.1:
        raise ValueError('jsonrpc 1.1 request required')
    if 'method' not in request or 'params' not in request:
        raise ValueError('method or parameters not given')
    method = request['method']
    params = request['params']
    if isinstance(params, list):
        args = tuple(params)
        kwargs = {}
    elif isinstance(params, dict):
        args = {}
        kwargs = {}
        for key, value in params.iteritems():
            if key.isdigit():
                args[int(key)] = value
            else:
                kwargs[key] = value
        try:
            args = tuple(args[idx] for idx in xrange(len(args)))
        except IndexError:
            raise ValueError('invalid parameter definition')
    id = request.get('id')
    return method, args, kwargs, id


def dump_datetime(d):
    """Creates a string for the datetime object a javascript
    function can parse. You just need to pass the resuling string
    on the client to ``new Date()``."""
    return d.strftime('%m %d %Y %H:%M:%S UTC')


def parse_datetime(d):
    """Takes a javascript dateformat (``new Date().toGMTString()``)
    string and returns a valid datetime object."""
    try:
        _, day, month, year, time, _ = d.split()
        hours, minutes, seconds = time.split(':')
        return datetime(
            int(year),
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
             'Aug', 'Sep', 'Nov', 'Dec'].index(month) + 1,
            int(day),
            int(hours),
            int(minutes),
            int(seconds)
        )
    except ValueError:
        raise ValueError('not a valid date string')
