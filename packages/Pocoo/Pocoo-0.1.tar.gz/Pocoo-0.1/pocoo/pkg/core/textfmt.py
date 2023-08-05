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

    def parse(self, text, signature):
        """
        Parse the input string and return HTML.

        :param signature: If this is ``True`` the pocoo wants to parse
                          a signature. For BBCode there could be special
                          rules like allowed and disallowed tags etc.
        """

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


class PlainText(MarkupFormat):
    """
    This parser just breaks lines and creates links.
    """
    name = 'plain'

    def parse(self, text, signature):
        #TODO: highlight quoted lines like heise does
        text = escape_html(text)
        text = nl2br(text)
        text = replace_smilies(self.ctx, text)
        return urlize(text, 50, True)

    def quote_text(self, req, text, username=None):
        lines = [u'> %s' % line for line in text.splitlines()]
        if username is not None:
            _ = req.gettext
            lines.insert(0, (_('%s has written') + u':') % username)
        return u'\n'.join(lines)


def frozen_translation(value=None):
    """
    A frozen translation for parsed texts::

        >>> _ = frozen_translation("blackbird")
        >>> _('%s wrote:')
        u'<trans value="blackbird">%s wrote</trans>'

    XXX: This method just supports one value and singular only.
    """
    attr = ''
    if value is not None:
        attr = ' value=%s' % quoteattr(value)
    def proxy(text):
        return u'<trans%s>%s</trans>' % (attr, escape_html(text))
    return proxy


def parse(ctx, text, signature=False, syntax_parser=None):
    """
    Parse ``text`` with the parser defined in the
    pocoo configuration or with the parser with the
    name ``syntax_parser``, and replace smilies.

    Translations will remain untouched.
    """
    if not isinstance(text, unicode):
        text = unicode(text)

    if syntax_parser is None:
        syntax_parser = ctx.cfg.get('board', 'syntax_parser', 'plain')
    syntax_parser = syntax_parser.lower()
    for comp in ctx.get_components(MarkupFormat):
        if comp.name == syntax_parser:
            return comp.parse(text, signature)
    else:
        raise ValueError('Parser "%s" not found' % syntax_parser)


def translate(req, text):
    """
    Translate parsed ``text``. Normally you would cache the
    parsed data in the database and translate it when the user
    requests it.
    """
    # if the request is set to None we just dummy translate it
    translatefunc = req and req.gettext or (lambda x: x)

    def handle_match(match):
        value = unescape_html(match.group(1))
        text = unescape_html(match.group(2))
        if value is not None:
            return translatefunc(text) % value
        return translatefunc(text)

    return frozen_translation_re.sub(handle_match, text)


def parse_and_translate(ctx_or_request, text, signature=False,
                        syntax_parser=None):
    """
    Parse and translate ``text``.

    Give it a context object to get an dummy translated version or
    pass a request object to it to get a real translation if
    possible.
    """
    if isinstance(ctx_or_request, Request):
        req = ctx_or_request
        ctx = req.ctx
    else:
        req = None
        ctx = ctx_or_request
    text = parse(ctx, text, signature, syntax_parser)
    return translate(req, text)


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
    from pocoo.utils import json

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
