#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Pocoo Gettext
    ~~~~~~~~~~~~~

    Searches for translatable strings in the whole pocoo package.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import os
import sys
from optparse import OptionParser
from compiler import parse, ast
from datetime import datetime
from array import array

import pocoo
from pocoo.context import ApplicationContext
from pocoo.utils.path import path as Path
from pocoo.pkg.core.i18n import TranslatableTag

from jinja import Template
from jinja.loader import BaseLoader
from jinja.lib import stdlib
from jinja.tags import ExtendsTag
from jinja import nodes as n


root = os.environ.get('POCOO_ROOT', '')
if not root:
    root = os.path.join(os.path.dirname(__file__), '..', 'instance')
context = ApplicationContext(os.path.abspath(root), is_cgi=True)


class FakeExtendsTag(n.Node):
    rules = {
        'default': [n.KeywordNode('extends'), n.ValueNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        pass

    def render(self):
        return ''

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class FakeLoader(BaseLoader):

    def __init__(self):
        self.charset = 'utf-8'

    def load(self, tpl, parent=None):
        if isinstance(tpl, unicode):
            return tpl
        return unicode(tpl, self.charset)

    def load_and_compile(self, name, lib=None, parent=None):
        return super(FakeLoader, self).load_and_compile(name, lib, parent)


savelib = context._template_lib.clone()
savelib.register_tag(TranslatableTag)
savelib.unregister_tag(ExtendsTag)
savelib.register_tag(FakeExtendsTag)


PO_HEADER = """#
# Pocoo Language File
#
msgid ""
msgstr ""
"Project-Id-Version: Pocoo %(version)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: utf-8\\n"
"Generated-By: %(filename)s\\n"
"""

EMPTY_STRING = ''
EMPTY_LINE = ['""\n']
LINE_SHIFT = ['\\n"\n"']


class StringCollection(object):

    def __init__(self):
        self.db = {}
        self.order = []

    def feed(self, file, line, string):
        if string not in self.db:
            self.db[string] = [(file, line)]
            self.order.append(string)
        else:
            self.db[string].append((file, line))

    def __iter__(self):
        for string in self.order:
            yield string, self.db[string]


def quote(s):
    """
    Quotes a given string so that it is useable in a .po file.
    """
    result = ['"']
    firstmatch = True
    for char in s:
        if char == '\n':
            if firstmatch:
                result = EMPTY_LINE + result
                firstmatch = False
            result += LINE_SHIFT
            continue
        if char in '\t"':
            result.append('\\')
        result.append(char)
    result.append('"')
    return EMPTY_STRING.join(result)


def scan_python_gettext(nodelist, calls):
    """
    Starts a CallFunc lookup in an ast tree.
    It returns a list of (lineno, string) tuples.
    """
    for node in nodelist:
        if isinstance(node, ast.CallFunc):
            handle = False
            for pos, n in enumerate(node):
                if pos == 0:
                    if isinstance(n, ast.Name) and n.name in calls:
                        handle = True
                elif pos == 1:
                    if handle:
                        yield n.lineno, n.value
                        break
                    else:
                        for line in scan_python_gettext([n], calls):
                            yield line
        elif hasattr(node, '__iter__'):
            for n in scan_python_gettext(node, calls):
                yield n


def scan_template_gettext(nodelist):
    """
    Returns all translateable texts from a given
    jinja nodelist.
    """
    for node in nodelist.findnodes():
        if isinstance(node, TranslatableTag):
            yield None, node.msgid


def scan_python_file(filename, calls):
    """
    Scan a python file for gettext calls.
    """
    fp = file(filename)
    try:
        code = parse(fp.read())
    except:
        print >> sys.stderr, 'Syntax Error in file %r' % filename
        fp.close()
    else:
        fp.close()
        return scan_python_gettext(code, calls)


def scan_template_file(filename):
    """
    Scan a template file for gettext calls.
    """
    fp = file(filename)
    c = fp.read()
    fp.close()
    t = Template(c, FakeLoader(), savelib)
    return scan_template_gettext(t.nodelist)


def scan_tree(pathname, calls=['_']):
    """
    Scans a tree for translatable strings.
    """
    path = Path(pathname)
    out = StringCollection()
    for f in path.walk('*.py'):
        result = scan_python_file(f, calls)
        if result is not None:
            for lineno, string in result:
                out.feed(f, lineno, string)
    #XXX: many false positives. what about scanning just the template dirs?
    for ext in ('html', 'txt'):
        for f in path.walk('*.%s' % ext):
            result = scan_template_file(f)
            if result is not None:
                for lineno, string in result:
                    out.feed(f, lineno, string)
    for line in out:
        yield line


class CommandlineApplication(object):

    def __init__(self):
        usage = "nothing till now"
        parser = OptionParser(usage)
        register = parser.add_option
        register(
            '-c', '--create', dest='create', action='store_true',
            help='Create an empty gettext template.'
        )

        self.options, self.args = parser.parse_args()

    def fail(self, msg=None):
        """Print error message."""
        if msg:
            print msg
        else:
            print "no action given. try -h for more information."
        sys.exit(1)

    def create_pot(self):
        """Print pot to stdout"""
        #XXX: allow the use of base gettext files
        base = None

        basepath = Path(pocoo.__file__).dirname()
        print PO_HEADER % {
            'time': datetime.now(),
            'filename': sys.argv[0],
            'version': pocoo.__version__
        }
        for string, occurrences in scan_tree(basepath):
            for path, lineno in occurrences:
                name = path[len(basepath):].lstrip('/')
                print '#. file %r, line %s' % (name, lineno or '?')
            print 'msgid %s' % quote(string)
            if base is None:
                print 'msgstr ""'
            else:
                s = base.gettext(string)
                if s == string:
                    s = ''
                print 'msgstr %s' % quote(s)
            print

    @staticmethod
    def run(self=None):
        """Start CLI application."""
        if self:
            if self.options.create:
                self.create_pot()
            else:
                self.fail()
        else:
            app = CommandlineApplication()
            app.run(app)


CommandlineApplication.run()
