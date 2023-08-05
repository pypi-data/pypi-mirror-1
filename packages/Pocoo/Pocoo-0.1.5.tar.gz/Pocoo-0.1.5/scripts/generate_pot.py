#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Pocoo Gettext Generator
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import __builtin__

import sys
import re
import compiler
import pocoo
import gettext
from pocoo.utils.path import Path
from pocoo.template import template_lib
from pocoo.pkg.core.i18n import TranslatableTag
from jinja import Template, StringLoader
from jinja.tags import ExtendsTag
from jinja import nodes as n
from compiler import ast
from datetime import datetime


PO_HEADER = """\
#
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
"Generated-By: %(filename)s\\n"\n
"""


def gettext_quote(s):
    result = ['"']
    firstmatch = True
    for char in s:
        if char == '\n':
            if firstmatch:
                result = ['""\n'] + result
                firstmatch = False
            result += ['\\n"\n"']
            continue
        if char in '\t"':
            result.append('\\')
        result.append(char)
    result.append('"')
    return ''.join(result)


class FakeExtendsTag(n.Node):
    rules = {
        'default': [n.KeywordNode('extends'), n.ValueNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        pass

    def render(self, context):
        return ''

    def __repr__(self):
        return '<FakeExtendsTag>'


savelib = template_lib.clone()
savelib.unregister_tag(ExtendsTag)
savelib.register_tag(FakeExtendsTag)


class DirectoryWalker(object):

    def __init__(self, root):
        self._root = Path(root)
        self._handlers = {}
        self._processor = None

    def add_handler(self, regex, handler):
        regex = re.compile(regex)
        self._handlers.setdefault(regex, []).append(handler)

    def set_processor(self, processor):
        self._processor = processor

    def log(self, msg):
        sys.stderr.write(msg)

    def run(self):
        if self._processor is None:
            raise RuntimeError('No processor defined')
        for filename in self._root.walk():
            filename = self._root.joinpath(filename).realpath()
            for regex, handlers in self._handlers.iteritems():
                m = regex.search(filename)
                if m is not None:
                    for handler in handlers:
                        ##try:
                        h = handler(self, filename)
                        shortname = filename[len(self._root.realpath()) + 1:]
                        for line in h():
                            self._processor.feed(shortname, line)
                        ##except Exception, e:
                        ##    self.log('Error: %s' % e)


class PythonHandler(object):
    calls = ('_', 'i18n')

    def __init__(self, walker, filename):
        self._filename = filename
        self._nodelist = compiler.parseFile(self._filename)

    def __call__(self, nodes=None):
        if nodes is None:
            nodes = self._nodelist
        for node in nodes:
            if isinstance(node, ast.CallFunc):
                handle = False
                lineno = 0
                args = []
                for pos, n in enumerate(node):
                    if pos == 0:
                        if isinstance(n, ast.Name) and n.name in self.calls:
                            handle = True
                            lineno = n.lineno
                    else:
                        if handle and hasattr(n, 'value'):
                            args.append(n.value)
                        else:
                            for line in self([n]):
                                yield line
                if handle:
                    args.insert(0, lineno)
                    yield args
            elif hasattr(node, '__iter__'):
                for line in self(node):
                    yield line


class JinjaHandler(object):

    def __init__(self, walker, filename):
        fp = file(filename)
        t = Template(fp.read(), StringLoader(), savelib)
        fp.close()
        self._filename = filename
        self._nodelist = t.nodelist

    def __call__(self):
        for node in self._nodelist.findnodes():
            if isinstance(node, TranslatableTag):
                if node.msgid_plural:
                    yield '?', node.msgid, node.msgid_plural
                else:
                    yield '?', node.msgid


class StringCollection(object):

    def __init__(self):
        self._db = {}
        self._order = []

    def feed(self, filename, linenumber, msgid, plural=None, amount=1):
        key = (msgid, plural)
        if key not in self._db:
            self._db[key] = [(filename, linenumber)]
            self._order.append(key)
        else:
            self._db[key].append((filename, linenumber))

    def __iter__(self):
        for key in self._order:
            msgid, plural = key
            yield msgid, plural, self._db[key]


class GettextProcessor(object):

    def __init__(self, base=None):
        self._db = StringCollection()
        if base is not None:
            fp = file(base)
            translator = gettext.GNUTranslations(fp)
            translator.set_output_charset('utf-8')
            self._base = lambda s: gettext_quote(translator.gettext(s))
        else:
            self._base = lambda s: '""'

    def feed(self, filename, line):
        self._db.feed(filename, *line)

    def print_result(self, stream=None):
        if stream is None:
            stream = sys.stdout
        stream.write(PO_HEADER % {
            'time':     datetime.now(),
            'filename': sys.argv[0],
            'version':  pocoo.__version__
        })
        for msgid, plural, occurrences in self._db:
            for filename, linenumber in occurrences:
                stream.write('#: %s:%s\n' % (filename, linenumber))
            if plural:
                stream.write('#, c-format\n')
            stream.write('msgid %s\n' % gettext_quote(msgid))
            if plural:
                stream.write('msgid_plural %s\n' % gettext_quote(plural))
            stream.write('msgstr %s\n\n' % self._base(msgid))


def main():
    if len(sys.argv) == 2:
        processor = GettextProcessor(sys.argv[1])
    else:
        processor = GettextProcessor()
    root = Path(pocoo.__file__).dirname()
    walker = DirectoryWalker(root)
    walker.add_handler(r'\.py$', PythonHandler)
    walker.add_handler(r'\.html$', JinjaHandler)
    walker.set_processor(processor)
    walker.run()
    processor.print_result()


if __name__ == '__main__':
    main()
