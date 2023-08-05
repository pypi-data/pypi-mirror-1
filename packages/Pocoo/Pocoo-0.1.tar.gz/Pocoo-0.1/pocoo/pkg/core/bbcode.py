# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.bbcode
    ~~~~~~~~~~~~~~~~~~~~~

    Pocoo BBCode parser.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import re

from pocoo import Component
from pocoo.pkg.core.textfmt import MarkupFormat, frozen_translation
from pocoo.utils.html import escape_html, translate_color
from pocoo.pkg.core.smilies import get_smiley_buttons, replace_smilies

tag_re = re.compile(r'(\[(/?[a-zA-Z0-9]+)(?:=(&quot;.+?&quot;|.+?))?\])')


class EndOfText(Exception):
    pass


class TokenList(list):

    def flatten(self):
        return u''.join(token.raw for token in self)


class Token(object):

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.raw
        )


class TextToken(Token):

    def __init__(self, data):
        self.data = self.raw = data


class TagToken(Token):

    def __init__(self, raw, tagname, attr):
        self.raw = raw
        self.name = tagname
        self.attr = attr


class NodeList(list):

    def render(self, ctx):
        return u''.join(node.render(ctx) for node in self)


class Node(object):

    def __init__(self, data):
        self.data = data

    def render(self, ctx):
        return self.data or u''

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.data
        )


class TextNode(Node):

    def render(self, ctx):
        text = replace_smilies(ctx, self.data)
        return u'<br />\n'.join(line.strip() for line in text.splitlines())


class Parser(object):

    def __init__(self, text, handlers):
        self._tokens = tag_re.split(text)
        self._tokens.reverse()
        self._is_text = True
        self._cache = []
        self._handlers = handlers

    def get_next_token(self):
        if self._cache:
            return self._cache.pop()
        get_token = self._tokens.pop
        if not self._tokens:
            raise EndOfText()
        if self._is_text:
            self._is_text = False
            return TextToken(get_token())
        else:
            self._is_text = True
            raw = get_token()
            tagname = get_token().lower()
            attr = get_token()
            if attr and attr[:6] == attr[-6:] == '&quot;':
                attr = attr[6:-6]
            return TagToken(raw, tagname, attr)

    def push_token(self, token):
        self._cache.append(token)

    def parse(self, needle=None):
        result = NodeList()
        try:
            while True:
                token = self.get_next_token()
                if isinstance(token, TagToken) and token.name == needle:
                    break
                result.append(self.get_node(token))
        except EndOfText:
            pass
        return result

    def get_tokens(self, needle=None):
        result = TokenList()
        try:
            while True:
                token = self.get_next_token()
                if isinstance(token, TagToken) and token.name == needle:
                    break
                result.append(token)
        except EndOfText:
            pass
        return result

    def render(self, ctx):
        return self.parse().render(ctx)

    def get_node(self, token):
        if isinstance(token, TextToken):
            return TextNode(token.data)
        if token.name in self._handlers:
            rv = self._handlers[token.name].get_node(token, self)
            if isinstance(rv, Node):
                return rv
            return Node(rv)
        return TextNode(token.raw)


class BBCodeTagProvider(Component):
    #: list of handled tags
    tags = []

    def get_node(self, tagname, parser):
        """
        Is called when a tag is found. It must return a valid ``Node``
        or a string which is automatically wrapped into a plain ``Node``.
        """

    def get_button(self, req, tagname):
        """
        Return a valid button definition for "tagname" or
        None if no button is required.

        A valid button definition is a dict in the following
        form::

            {'name':        _('Bold'),
             'description': _('Insert bold text'),
             'icon':        self.ctx.make_url('!cobalt/...'),
             'insert':      '[b]{text}[/b]'}
        """


class BBCode(MarkupFormat):
    """
    BBCode markup format.
    """
    name = 'bbcode'
    editor_javascript = '!cobalt/core/pocoo/app/BBCodeEditor.js'

    def __init__(self, ctx):
        super(BBCode, self).__init__(ctx)
        self.handlers = {}
        for comp in ctx.get_components(BBCodeTagProvider):
            for tag in comp.tags:
                self.handlers[tag] = comp

    def get_signature_tags(self):
        """Returns the allowed signature tags or None if all"""
        if not hasattr(self, '_signature_tags'):
            r = self.ctx.cfg.get('board', 'bbcode_signature_tags', 'ALL')
            if r == 'ALL':
                self._signature_tags = None
            else:
                self._signature_tags = [s.strip().lower() for s in r.split(',')]
        return self._signature_tags

    @property
    def signature_handlers(self):
        if not hasattr(self, '_signature_handlers'):
            self._signature_handlers = {}
            for tag in self.get_signature_tags():
                if tag in self.handlers:
                    self._signature_handlers[tag] = self.handlers[tag]
        return self._signature_handlers

    def parse(self, text, signature):
        if signature:
            handlers = self.signature_handlers
        else:
            handlers = self.handlers
        parser = Parser(escape_html(text), handlers)
        return parser.render(self.ctx)

    def quote_text(self, req, text, username=None):
        if username is None:
            return '[quote]%s[/quote]' % text
        return '[quote="%s"]%s[/quote]' % (username, text)

    def get_editor_options(self, req, signature):
        buttons = []
        if signature:
            signature_tags = self.get_signature_tags()
        for comp in self.ctx.get_components(BBCodeTagProvider):
            for tagname in comp.tags:
                if signature and signature_tags is not None and\
                   tagname not in signature_tags:
                    continue
                btn = comp.get_button(req, tagname)
                if btn is not None:
                    buttons.append(btn)
        return {
            'buttons':  buttons,
            'smilies':  get_smiley_buttons(req.ctx)
        }


class BasicBBCodeTagProvider(BBCodeTagProvider):
    tags = ['b', 'i', 'u', 's', 'url', 'email', 'color', 'size',
            'code', 'quote', 'list']

    def get_node(self, token, parser):
        ctx = self.ctx
        if token.name == 'b':
            nodelist = parser.parse('/b')
            return u'<strong>%s</strong>' % nodelist.render(ctx)
        if token.name == 'i':
            nodelist = parser.parse('/i')
            return u'<em>%s</em>' % nodelist.render(ctx)
        if token.name == 'u':
            nodelist = parser.parse('/u')
            return u'<ins>%s</ins>' % nodelist.render(ctx)
        if token.name == 's':
            nodelist = parser.parse('/s')
            return u'<del>%s</del>' % nodelist.render(ctx)
        if token.name == 'url':
            if token.attr:
                nodelist = parser.parse('/url')
                content = nodelist.render(ctx)
                url = token.attr
            else:
                tokenlist = parser.get_tokens('/url')
                content = url = tokenlist.flatten()
            if url.startswith('javascript:'):
                url = url[11:]
            return u'<a href="%s" rel="nofollow">%s</a>' % (url, content)
        if token.name == 'email':
            if token.attr:
                nodelist = parser.parse('/email')
                content = nodelist.render(ctx)
                mail = token.attr
            else:
                tokenlist = parser.get_tokens('/email')
                mail = content = tokenlist.flatten()
            return u'<a href="mailto:%s">%s</a>' % (mail, content)
        if token.name == 'color':
            nodelist = parser.parse('/color')
            content = nodelist.render(ctx)
            try:
                color = translate_color(token.attr)
            except ValueError:
                return token.raw
            return u'<span style="color: %s">%s</span>' % (color, content)
        if token.name == 'size':
            nodelist = parser.parse('/size')
            content = nodelist.render(ctx)
            if not token.attr or not token.attr.isdigit() or len(token.attr) > 2:
                return token.raw
            return u'<span style="font-size: %spx">%s</span>' % (token.attr, content)
        if token.name == 'img':
            tokenlist = parser.get_tokens('/img')
            url = tokenlist.flatten()
            if url.startswith('javascript:'):
                url = url[11:]
            return u'<img src="%s" />' % url
        if token.name == 'code':
            tokenlist = parser.get_tokens('/code')
            return u'<pre>%s</pre>' % tokenlist.flatten()
        if token.name == 'quote':
            nodelist = parser.parse('/quote')
            if token.attr:
                _ = frozen_translation(token.attr)
                preamble = u'<div class="written_by">%s</div>' % _('%s has written:')
            else:
                preamble = u''
            return u'<blockquote>%s%s</blockquote>' % (preamble, nodelist.render(ctx))
        if token.name == 'list':
            nodelist = parser.parse('/list')
            lines = []
            for line in re.split(r'^\s*\[\*\](?m)', u'\n%s\n' % nodelist.render(ctx)):
                line = line.strip()
                lines.append(u'<li>%s</li>' % line)
            return u'<ul>%s</ul>' % u'\n'.join(lines)

    def get_button(self, req, tagname):
        _ = req.gettext
        make_url = self.ctx.make_url
        values = labels = None
        # XXX: This should be made a dictionary.
        if tagname == 'b':
            name = _('Bold')
            description = _('Insert bold text')
            icon = 'bold.png'
            insert = '[b]{text}[/b]'
        elif tagname == 'i':
            name = _('Italic')
            description = _('Insert italic text')
            icon = 'italic.png'
            insert = '[i]{text}[/i]'
        elif tagname == 'u':
            name = _('Underline')
            description = _('Insert underlined text')
            icon = 'underline.png'
            insert = '[u]{text}[/u]'
        elif tagname == 'size':
            name = _('Font Size')
            description = _('Change font size')
            icon = None
            insert = '[size={attr}]{text}[/size]'
            labels = [_("Tiny"), _("Small"), _("Normal"), _("Big"), _("Huge")]
            values = [8, 11, 13, 18, 24]
        elif tagname == 'color':
            name = _('Font Color')
            description = _('Change font color')
            icon = None
            insert = '[color={attr}]{text}[/color]'
            labels = [_('Black'), _('Blue'), _('Brown'), _('Cyan'), _('Gray'),
                      _('Green'), _('Magenta'), _('Purple'), _('Red'), _('White'),
                      _('Yellow')]
            values = ['black', 'blue', 'brown', 'cyan', 'gray', 'green', 'magenta',
                      'purple', 'red', 'white', 'yellow']
        elif tagname == 's':
            name = _('Strikethrough')
            description = _('Strikethrough')
            icon = 'strikethrough.png'
            insert = '[s]{text}[/s]'
        elif tagname == 'url':
            name = _('Link')
            description = _('Create a link')
            icon = 'link.png'
            insert = '[url]{text}[/url]'
        elif tagname == 'email':
            name = _('Email')
            description = _('Create a email link')
            icon = 'mail.png'
            insert = '[email]{text}[/email]'
        elif tagname == 'img':
            name = _('Image')
            description = _('Insert an image')
            icon = 'img.png'
            insert = '[img]{text}[/img]'
        elif tagname == 'code':
            name = _('Code')
            description = _('Insert code')
            icon = 'code.png'
            insert = '[code]{text}[/code]'
        elif tagname == 'quote':
            name = _('Quote')
            description = _('Insert a quote')
            icon = 'quote.png'
            insert = '[quote]{text}[/quote]'
        else:
            return
        iconurl = '!cobalt/core/default/img/bbcode/%s'
        return {
            'name':         str(name),
            'description':  str(description),
            # TODO: make this themeable
            'icon':         icon and str(make_url(iconurl % icon)),
            'insert':       str(insert),
            'values':       values,
            'labels':       labels
        }
