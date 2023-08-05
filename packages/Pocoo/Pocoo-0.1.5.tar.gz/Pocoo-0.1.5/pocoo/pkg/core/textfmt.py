# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.textfmt
    ~~~~~~~~~~~~~~~~~~~~~~

    Pocoo text processing interfaces.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
from xml.sax.saxutils import quoteattr

from pocoo.http import Request
from pocoo.utils.html import nl2br, escape_html, unescape_html, urlize
from pocoo import Component
from pocoo.pkg.core.smilies import replace_smilies
from pocoo.utils.activecache import Node, load_cache, generate_cache
from pocoo.utils import json


frozen_translation_re = re.compile(r'<trans(?: value="(.*?)")?>(.*?)</trans>')


class MarkupFormat(Component):
    """
    A text markup format, such as BBCode or HTML.
    """

    #: The relative path to the javascript file for the editor.
    editor_javascript = '!cobalt/core/PocooLib/BaseEditor.js'

    #: Name for this format. must be lowercase
    @property
    def name(self):
        return self.__class__.__name__.lower()

    def get_title(self, req):
        """
        Title of this formatter.
        """
        return self.name.lower()

    def parse(self, text, signature):
        """
        This method has to return either an activecache Node or an
        string/Unicode object.

        :param signature: If this is ``True`` the pocoo wants to parse
                          a signature. For BBCode there could be special
                          rules like allowed and disallowed tags etc.
        """

    def render_callback(self, req, callback, data):
        """
        If the ``parse`` method returns an activecache `CallbackNode`
        this method will be called for the define callback.
        """
        return u''

    def quote_text(self, req, text, username=None):
        """
        This has to quote a given text. For example a BBCode
        Markup Formatter should wrap the text in [quote].
        """
        return text

    def get_editor_options(self, req, signature):
        """
        This method has to return a dict of JSON
        serializable values which get passed to the
        function ``initEditor()`` which is defined
        in the editor javascript file.

        If `signature` is ``True`` pocoo requested an editor for the
        signature and wants just the editor definitions which are
        relevant for an working signature editor. See the ``BBCode``
        text formatter for an example.
        """
        return {}

    def get_text_plain(self, text):
        """
        This method has to return the simple plain text without any markup.
        That's needed by e.g. the search function.
        """
        return re.compile(r'<[^>]+>').sub('', text)


class PlainText(MarkupFormat):
    """
    This parser just breaks lines and creates links.
    """
    name = 'plain'

    def parse(self, text, signature):
        text = escape_html(text)
        text = nl2br(text)
        text = replace_smilies(self.ctx, text)
        return urlize(text, 50, True)

    def quote_text(self, req, text, username=None):
        lines = [u'> %s' % line for line in text.splitlines()]
        if username is not None:
            _ = req.gettext
            lines.insert(0, (_('%s wrote') + u':') % username)
        return u'\n'.join(lines)


def get_parser(ctx, syntax_parser=None):
    """
    Return the parser for a context.
    """
    if syntax_parser is None:
        syntax_parser = ctx.cfg.get('board', 'syntax_parser', 'plain')
    syntax_parser = syntax_parser.lower()
    for comp in ctx.get_components(MarkupFormat):
        if comp.name == syntax_parser:
            return comp
    else:
        raise ValueError('Parser "%s" not found' % syntax_parser)


def parse(ctx, text, signature=False, syntax_parser=None):
    """
    Parses an text and returns a marshalled object. You then can
    put such an string into the database or push it to the
    render function.
    """
    if not isinstance(text, unicode):
        text = unicode(text)
    text = type(text)('\n').join(text.splitlines())
    comp = get_parser(ctx, syntax_parser)
    node = comp.parse(text, signature)
    if isinstance(node, basestring):
        node = Node(node)
    return generate_cache(node, comp.name)


def get_text_plain(ctx, text, syntax_parser=None):
    """
    Return the plain text without markup (for example for the
    search function.
    """
    if not isinstance(text, unicode):
        text = unicode(text)
    comp = get_parser(ctx, syntax_parser)
    return comp.get_text_plain(text)


def render(req, data):
    """
    Renders a parsed data
    """
    node, syntax_parser = load_cache(data)
    comp = get_parser(req.ctx, syntax_parser)
    return node.render(req, comp)


def parse_and_render(req, text, signature=False, syntax_parser=None):
    """
    Parses and renders a text.
    """
    if not isinstance(text, unicode):
        text = unicode(text)
    text = type(text)('\n').join(text.splitlines())
    if syntax_parser is None:
        syntax_parser = req.ctx.cfg.get('board', 'syntax_parser', 'plain')
    syntax_parser = syntax_parser.lower()
    for comp in req.ctx.get_components(MarkupFormat):
        if comp.name == syntax_parser:
            node = comp.parse(text, signature)
            if isinstance(node, basestring):
                node = Node(node)
            return node.render(req, comp)
    else:
        raise ValueError('Parser "%s" not found' % syntax_parser)


def get_editor(req, signature=False, syntax_parser=None):
    """
    Return a tuple in the form (javascript_file, options)
    for the template. Both of them are strings which can be
    used directly in the template::

        <script type="text/javascript" src="{{ editorjs }}"></script>
        <script type="text/javascript">
            initEditor('id_of_textarea', 'id_of_toolbar', {{ options }});
        </script>

    If you set `signature` to ``True`` it will just display the
    buttons which are relevant for the signature editor.
    """
    if syntax_parser is None:
        syntax_parser = req.ctx.cfg.get('board', 'syntax_parser', 'plain').lower()
    for comp in req.ctx.get_components(MarkupFormat):
        if comp.name == syntax_parser:
            js = req.ctx.make_url(comp.editor_javascript)
            options = json.dumps(comp.get_editor_options(req, signature))
            return js, options
    raise ValueError('Parser "%s" not found' % syntax_parser)


def quote_text(req, text, username=None, syntax_parser=None):
    """Quote ``text`` with the style defined in the markup parser."""
    if syntax_parser is None:
        syntax_parser = req.ctx.cfg.get('board', 'syntax_parser', 'plain').lower()
    for comp in req.ctx.get_components(MarkupFormat):
        if comp.name == syntax_parser:
            return comp.quote_text(req, text, username)
    raise ValueError('Parser "%s" not found' % syntax_parser)


def get_markup_formatters(req):
    """
    Return a list of known formatters
    """
    result = []
    for comp in req.ctx.get_components(MarkupFormat):
        result.append((comp.name, comp.get_title(req)))
    result.sort(key=lambda x: x[1].lower())
    return result
