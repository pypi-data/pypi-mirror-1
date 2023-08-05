# -*- coding: utf-8 -*-
"""
    pocoo.utils.decorators
    ~~~~~~~~~~~~~~~~~~~~~~

    Decorators and decorator utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
import inspect
import new
import itertools
import threading


class decorator(object):
    """
    General purpose decorator factory: takes a caller function as
    input and returns a decorator. A caller function is any
    function like this::

        def caller(func, *args, **kw):
            # do something
            return func(*args, **kw)
    """
    def __init__(self, caller):
        self.caller = caller

    def __call__(self, func):
        return self._decorate(func, self.caller)

    def _getinfo(self, func):
        assert inspect.ismethod(func) or inspect.isfunction(func)
        regargs, varargs, varkwargs, defaults = inspect.getargspec(func)
        argnames = list(regargs)
        if varargs:
            argnames.append(varargs)
        if varkwargs:
            argnames.append(varkwargs)
        counter = itertools.count()
        fullsign = inspect.formatargspec(
            regargs, varargs, varkwargs, defaults,
            formatvalue=lambda value: '=defarg[%i]' % counter.next())[1:-1]
        shortsign = inspect.formatargspec(
            regargs, varargs, varkwargs, defaults,
            formatvalue=lambda value: '')[1:-1]
        dic = dict(('arg%s' % n, name) for n, name in enumerate(argnames))
        dic.update(name=func.__name__, argnames=argnames, shortsign=shortsign,
            fullsign = fullsign, defarg = func.func_defaults or ())
        return dic

    def _decorate(self, func, caller):
        """
        Takes a function and a caller and returns the function
        decorated with that caller. The decorated function is obtained
        by evaluating a lambda function with the correct signature.
        """
        infodict = self._getinfo(func)
        if '__call_' in infodict['argnames'] or\
           '__func_' in infodict['argnames']:
            raise NameError, "You cannot use __call_ or __func_ as argument names!"
        execdict = dict(__func_=func, __call_=caller, defarg=func.func_defaults or ())
        if func.__name__ == "<lambda>":
            lambda_src = "lambda %(fullsign)s: __call_(__func_, %(shortsign)s)" \
                        % infodict
            dec_func = eval(lambda_src, execdict)
        else:
            func_src = """def %(name)s(%(fullsign)s):
            return __call_(__func_, %(shortsign)s)""" % infodict
            exec func_src in execdict
            dec_func = execdict[func.__name__]
        dec_func.__doc__ = func.__doc__
        dec_func.__dict__ = func.__dict__
        return dec_func


def copyfunc(func):
    """
    Create an independent copy of a function.
    """
    return new.function(func.func_code, func.func_globals, func.func_name,
                        func.func_defaults, func.func_closure)


@decorator
def memoize(func, *args):
    """
    This decorator implements the memoize pattern, i.e. it caches
    the result of a function call in a dictionary, so that the
    next time the function is called with the same parameters the
    result is retrieved from the cache and not recomputed.
    """
    try:
        d = getattr(func, 'memoize_dict')
    except AttributeError:
        func.memoize_dict = {}
        d = func.memoize_dict
    if args in d:
        return d[args]
    else:
        result = func(*args)
        d[args] = result
        return result


@decorator
def background(func, *args):
    """
    Run a function in the background.
        Returns a ThreadController object providing a
        running and result property.
    """
    class BackgroundThread(threading.Thread):
        def __init__(self):
            super(BackgroundThread, self).__init__()
            self.running = False
            self.result = None

        def run(self):
            self.running = True
            self.result = func(*args)
            self.running = False

    class ThreadController(object):

        def __init__(self, thread):
            self.thread = thread

        def _get_result(self):
            if self.thread.running:
                raise RuntimeError, 'Thread still running'
            return self.thread.result

        running = property(lambda s: s.thread.running)
        result = property(_get_result)

    t = BackgroundThread()
    t.start()
    return ThreadController(t)


class TailRecurseException(Exception):
    """
    Helper exception for `tail_call_optimized` below.
    """


@decorator
def tail_call_optimized(func, *args):
    """
    This function decorates a function with tail call optimization. It does
    this by throwing an exception if it is it's own grandparent, and catching
    such exceptions to fake the tail call optimization.

    This function fails if (and only if) the decorated function recurses in a
    non-tail context.
    """
    # from littlelanguages.com:
    # http://littlelanguages.com/2006/02/tail-call-optimization-as-python.html
    f = sys._getframe()
    if f.f_back and f.f_back.f_back and\
       f.f_back.f_back.f_code == func.func_code:
        raise TailRecurseException(*args)
    while True:
        try:
            return func(*args)
        except TailRecurseException, e:
            args = e.args
