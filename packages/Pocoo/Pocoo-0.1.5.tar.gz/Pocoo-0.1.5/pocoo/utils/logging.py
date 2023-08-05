# -*- coding: utf-8 -*-
"""
    pocoo.utils.logging
    ~~~~~~~~~~~~~~~~~~~

    Pocoo logging module.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
from datetime import datetime


class Logger(object):
    """
    Generic logging class.
    """

    def __init__(self, ctx=None, stream=None, timeformat='%H:%M:%S', system=''):
        if stream is not None:
            self._stream = stream
        elif ctx is not None:
            stream = ctx.cfg.get('development', 'log_output', 'stderr')
            if not stream or stream == 'None':
                self._stream = None
            elif stream == 'stdout':
                self._stream = sys.stdout
            elif stream == 'stderr':
                self._stream = sys.stderr
            else:
                self._stream = file(stream, 'w+')
        else:
            self._stream = sys.stderr
        self._timeformat = timeformat
        self._system = system
        self._write = self._stream.write
        if hasattr(self._stream, 'flush'):
            self._flush = self._stream.flush
        else:
            self._flush = lambda: None

    def log(self, msg):
        self._log(1, self._system, msg)

    def info(self, msg):
        self._log(2, self._system, msg)

    def warn(self, msg):
        self._log(3, self._system, msg)

    def fail(self, msg):
        self._log(4, self._system, msg)

    def _log(self, level, system, msg):
        time = datetime.now().strftime(self._timeformat)
        lv = { 0: '',
               1: 'i ',
               2: 'I ',
               3: 'W ',
               4: 'E ' }.get(level, '? ')
        self._write('%s[%s] %s: %s\n' % (lv, time, system, msg))
        self._flush()
