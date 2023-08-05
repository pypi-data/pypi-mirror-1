# -*- coding: utf-8 -*-
"""
    pocoo.utils.debug
    ~~~~~~~~~~~~~~~~~

    Implements a simple debugging toolkit.

    Usage example::

        from pocoo.utils.debug import use_dtk, dtk

        use_dtk()
        dtk.log('source', 'important message')

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
import time

from pocoo.utils.logging import Logger


class DtkBase(object):

    def __init__(self):
        self._logger = Logger(stream=sys.stderr)

    def set_output(self, ctx):
        self._logger = Logger(ctx=ctx)


class FakeDtk(DtkBase):

    def log(self, component, msg, *args):
        pass

    def trace(self, func):
        return func

    def trace_time(self, func):
        return func

    def trace_if_return(self, condition):
        return lambda func: func

    def trace_if_exc(self, func):
        return func


class RealDtk(DtkBase):

    def log(self, component, msg, *args):
        self._logger._log(0, component, msg % args)

    def trace(self, func):
        """ Decorator.
        If debugging is enabled, wrap function to print arguments
        and return value.
        """
        name = func.func_name
        parent = sys._getframe(1).f_code.co_name
        def wrapper(*args, **kwargs):
            self.log(parent, '%s() called with %r, %r' % (name,
                                                          args, kwargs))
            ret = func(*args, **kwargs)
            if ret is not None:
                self.log(parent, '  ... returned %r' % ret)
            return ret
        wrapper.func_name = name
        wrapper.__doc__ = func.__doc__
        return wrapper

    def trace_time(self, func):
        """ Decorator.
        Print how long the function took to run.
        """
        name = func.func_name
        parent = sys._getframe(1).f_code.co_name
        def wrapper(*args, **kwargs):
            self.log(parent, '%s() called with %r, %r' % (name, args,
                     kwargs))
            t1 = time.time()
            ret = func(*args, **kwargs)
            t2 = time.time()
            self.log(parent, '  ... took %.4f' % (t2-t1))
            return ret
        wrapper.func_name = name
        wrapper.__doc__ = func.__doc__
        return wrapper

    def trace_if_return(self, condition):
        """ Decorator.
        Print trace information of decorated function only if the
        condition is true.
        """
        def decorator(func):
            name = func.func_name
            parent = sys._getframe(1).f_code.co_name
            def wrapper(*args, **kwargs):
                ret = func(*args, **kwargs)
                if eval('ret '+condition):
                    self.log(parent, '%s() called with %r, %r' % (name,
                             args, kwargs))
                    self.log(parent, '  ... returned %r' % ret)
                return ret
            wrapper.func_name = name
            wrapper.__doc__ = func.__doc__
            return wrapper
        return decorator

    def trace_if_exc(self, func):
        """ Decorator.
        Print trace information of function if it raises an exception.
        """
        name = func.func_name
        parent = sys._getframe(1).f_code.co_name
        def wrapper(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except Exception, exc:
                self.log(parent, '%s() called with %r, %r' % (
                         name, args, kwargs))
                self.log(parent, '  ... raised %r' % exc)
                raise
            else:
                return ret
        wrapper.func_name = name
        wrapper.__doc__ = func.__doc__
        return wrapper


dtk = FakeDtk()

def use_dtk(enable=True):
    if enable:
        dtk.__class__ = RealDtk
    else:
        dtk.__class__ = FakeDtk
