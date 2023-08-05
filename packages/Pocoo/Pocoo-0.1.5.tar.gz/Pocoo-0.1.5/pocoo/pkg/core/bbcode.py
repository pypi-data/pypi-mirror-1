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
from pocoo.pkg.core.textfmt import MarkupFormat
from pocoo.pkg.core.smilies import get_smiley_buttons, replace_smilies
from pocoo.utils.html import escape_html, translate_color
from pocoo.utils.activecache import Node, CallbackNode, NodeList

tag_re = re.compile(r'(\[(/?[a-zA-Z0-9]+)(?:=(&quot;.+?&quot;|.+?))?\])')


class EndOfText(Exception):
    """Raise when the end of the text is reached."""


class TokenList(list):
    """A subclass of a list for tokens which allows to flatten
    the tokens so that the original bbcode is the return value."""

    def flatten(self):
        return u''.join(token.raw for token in self)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            list.__repr__(self)
        )


class Token(object):
    """Token Baseclass"""

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.raw
        )


class TextToken(Token):
    """A token for plain text."""

    def __init__(self, data):
        self.data = self.raw = data


class TagToken(Token):
    """A token for tags."""

    def __init__(self, raw, tagname, attr):
        self.raw = raw
        self.name = tagname
        self.attr = attr


class Parser(object):
    """
    BBCode Parser Class
    """

    def __init__(self, ctx, text, handlers, allowed_tags):
        self.ctx = ctx
        self._tokens = tag_re.split(text)
        self._tokens.reverse()
        self._is_text = True
        self._cache = []
        self._handlers = handlers
        self._allowed_tags = allowed_tags

    def tag_allowed(self, tagname):
        """
        Check if a tagname is allowed for this parser.
        """
        if self._allowed_tags is None:
            return True
        return tagname in self._allowed_tags

    def get_next_token(self):
        """
        Fetch the next raw token from the text
        Raise ``EndOfText`` if not further token exists.
        """
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
        """
        Pushes the last fetched token in a cache so that the next time
        you call ``get_next_token`` returns the pushed token.
        """
        self._cache.append(token)

    def parse(self, needle=None, preserve_needle=False):
        """
        Parses the text until ``needle`` or the end of text if not defined.
        If it finds the needle it will delete the needle token. If you want
        the needle token too set ``preserve_needle`` to ``True``.

        In comparison with the ``get_tokens`` method this method will call
        the node handlers for each node.
        """
        result = NodeList()
        try:
            while True:
                token = self.get_next_token()
                if isinstance(token, TagToken) and token.name == needle:
                    if preserve_needle:
                        self.push_token(token)
                    break
                result.append(self.get_node(token))
        except EndOfText:
            pass
        return result

    def get_tokens(self, needle=None, preserve_needle=False):
        """
        Like ``parse`` but returns an unparsed TokenList. Basically you
        would never need this method except for preserved areas like
        Code blocks etc.
        """
        result = TokenList()
        try:
            while True:
                token = self.get_next_token()
                if isinstance(token, TagToken) and token.name == needle:
                    if preserve_needle:
                        self.push_token(token)
                    break
                result.append(token)
        except EndOfText:
            pass
        return result

    def get_node(self, token):
        """
        Return the node for a token. If the token was a ``TextToken``
        the resulting node will call ``get_text_node`` which returns a
        \n to <br/> replaced version of the token value wrapped in a
        plain ``Node``. In all other cases it will try to lookup the node
        in the list of registered token handlers.

        If this fails it wraps the raw token value in a ``Node``.
        """
        if isinstance(token, TextToken):
            return self.get_text_node(token.data)
        if self.tag_allowed(token.name):
            for handler in self._handlers:
                rv = handler.get_node(token, self)
                if rv is not None:
                    if isinstance(rv, Node):
                        return rv
                    return Node(rv)
        return self.get_text_node(token.raw)

    def get_text_node(self, data):
        """
        Newline replaces the text and wraps it in an ``Node``.
        """
        text = replace_smilies(self.ctx, data)
        return Node(re.sub(r'\n', '<br />\n', text))

    def wrap_render(self, tag, parse_until):
        """
        Renders untile ``parse_until`` and wraps it in the html tag ``tag``.
        """
        return NodeList(Node('<%s>' % tag), self.parse(parse_until),
                        Node('</%s>' % tag))

    def joined_render(self, *args):
        """
        Takes a number of arguments which are either strings, unicode objects
        or nodes. It creates a new newlist, iterates over all arguments and
        converts all to nodes if not happened by now.
        """
        result = NodeList()
        for arg in args:
            if isinstance(arg, Node):
                result.append(arg)
            else:
                result.append(Node(arg))
        return result

    def callback(self, callback, data):
        """
        Returns a new ``CallbackNode``. Don't create callback nodes on your
        own, this method might do some further magic in the future.
        """
        return CallbackNode(callback, *data)


class BBCodeTagProvider(Component):
    #: list of handled tags
    tags = []

    #: list of callbacks
    callbacks = []

    def get_node(self, token, parser):
        """
        Is called when a tag is found. It must return a valid ``Node``
        or a string which is automatically wrapped into a plain ``Node``.
        """

    def render_callback(self, req, callback, data):
        """
        Has to handle a callback for ``callback`` with ``data`` and return a
        string
        """
        return u''

    def get_buttons(self, req):
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
        return ()


class BBCode(MarkupFormat):
    """
    BBCode markup format.
    """
    name = 'bbcode'
    editor_javascript = '!cobalt/core/pocoo/app/BBCodeEditor.js'

    def __init__(self, ctx):
        super(BBCode, self).__init__(ctx)
        self.handlers = {}
        self.callbacks = {}
        for comp in ctx.get_components(BBCodeTagProvider):
            for tag in comp.tags:
                self.handlers.setdefault(tag, []).append(comp)
            for callback in comp.callbacks:
                self.callbacks[callback] = comp

    def get_signature_tags(self):
        """Returns the allowed signature tags or None if all"""
        if not hasattr(self, '_signature_tags'):
            r = self.ctx.cfg.get('board', 'bbcode_signature_tags', 'ALL')
            if r == 'ALL':
                self._signature_tags = None
            else:
                self._signature_tags = [s.strip().lower() for s in r.split(',')]
        return self._signature_tags

    def parse(self, text, signature):
        handlers = self.ctx.get_components(BBCodeTagProvider)
        allowed_tags = None
        if signature:
            allowed_tags = self.get_signature_tags()
        p = Parser(self.ctx, escape_html(text), handlers, allowed_tags)
        return p.parse()

    def render_callback(self, req, callback, data):
        """Redirect the callback to the BBCode Provider."""
        for comp in self.ctx.get_components(BBCodeTagProvider):
            rv = comp.render_callback(req, callback, data)
            if rv is not None:
                return rv
        raise Exception('unhandled callback %r' % callback)

    def quote_text(self, req, text, username=None):
        if username is None:
            return '[quote]%s[/quote]' % text
        return '[quote="%s"]%s[/quote]' % (username, text)

    def get_editor_options(self, req, signature):
        buttons = []
        if signature:
            signature_tags = self.get_signature_tags()
        for comp in self.ctx.get_components(BBCodeTagProvider):
            for button in comp.get_buttons(req):
                if signature and button['tagname'] not in signature_tags:
                    continue
                buttons.append(button)
        return {
            'buttons':  buttons,
            'smilies':  get_smiley_buttons(req.ctx)
        }

    def get_text_plain(self, text):
        tag_re = re.compile(r'\[/?(%s)(=(".+?"|.+?))?\]' % '|'.join(
                            re.escape(tag) for tag in self.handlers))
        return tag_re.sub('', text)


class BasicBBCodeTagProvider(BBCodeTagProvider):
    tags = ['b', 'i', 'u', 's', 'url', 'email', 'color', 'size',
            'code', 'quote', 'list']
    callbacks = ['quote', 'list']

    def get_node(self, token, parser):
        ctx = self.ctx
        if token.name == 'b':
            if token.attr:
                return
            return parser.wrap_render('strong', '/b')
        if token.name == 'i':
            if token.attr:
                return
            return parser.wrap_render('em', '/i')
        if token.name == 'u':
            if token.attr:
                return
            return parser.wrap_render('ins', '/u')
        if token.name == 's':
            if token.attr:
                return
            return parser.wrap_render('del', '/s')
        if token.name == 'url':
            if token.attr:
                content = parser.parse('/url')
                url = token.attr
            else:
                tokenlist = parser.get_tokens('/url')
                content = url = tokenlist.flatten()
            if url.startswith('javascript:'):
                url = url[11:]
            return parser.joined_render('<a href="', url, '">', content, '</a>')
        if token.name == 'email':
            if token.attr:
                content = parser.parse('/email')
                mail = token.attr
            else:
                tokenlist = parser.get_tokens('/email')
                mail = content = tokenlist.flatten()
            return parser.joined_render('<a href="mailto:"', mail, '">',
                                        content, '</a>')
        if token.name == 'color':
            content = parser.parse('/color')
            try:
                color = translate_color(token.attr)
            except ValueError:
                return token.raw
            return parser.joined_render('<span style="color: ', color, '">',
                                        content, '</span>')
        if token.name == 'size':
            content = parser.parse('/size')
            if not token.attr or not token.attr.isdigit() or len(token.attr) > 2:
                return token.raw
            return parser.joined_render('<span style="font-size: ', token.attr,
                                        'px">', content, '</span>')
        if token.name == 'img':
            if token.attr:
                return
            tokenlist = parser.get_tokens('/img')
            url = tokenlist.flatten()
            if url.startswith('javascript:'):
                url = url[11:]
            return u'<img src="%s" />' % url
        if token.name == 'code':
            if token.attr:
                return
            return u'<pre>%s</pre>' % parser.get_tokens('/code').flatten()
        if token.name == 'quote':
            return parser.callback('quote', (token.attr or u'',
                                             parser.parse('/quote')))
        if token.name == 'list':
            return parser.callback('list', (token.attr or u'*',
                                            parser.parse('/list')))

    def render_callback(self, req, callback, data):
        if callback == 'quote':
            _ = req.gettext
            written, body = data
            if written:
                if not written.endswith(':'):
                    written = (_('%s wrote') % written) + u':'
                written = u'<div class="written_by">%s</div>' % written
            return u'<blockquote>%s%s</blockquote>' % (
                written, body.render(req, self)
            )
        if callback == 'list':
            type, body = data
            lines = []
            for line in re.split(r'^\s*\[\*\](?m)', body.render(req, self)):
                line = line.strip()
                if line:
                    lines.append(u'<li>%s</li>' % line)
            return u'<ul>%s</ul>' % u'\n'.join(lines)

    def get_buttons(self, req):
        _ = req.gettext
        make_url = self.ctx.make_url
        #XXX: themeable
        icon_url = lambda x: make_url('!cobalt/core/default/img/bbcode/' + x)

        return [
            {'tagname':         'b',
             'name':            _('Bold'),
             'description':     _('Insert bold text'),
             'insert':          '[b]{text}[/b]',
             'icon':            icon_url('bold.png')},
            {'tagname':         'i',
             'name':            _('Italic'),
             'description':     _('Insert italic text'),
             'insert':          '[i]{text}[/i]',
             'icon':            icon_url('italic.png')},
            {'tagname':         'u',
             'name':            _('Underline'),
             'description':     _('Insert underlined text'),
             'insert':          '[u]{text}[/u]',
             'icon':            icon_url('underline.png')},
            {'tagname':         's',
             'name':            _('Strikethrough'),
             'description':     _('Insert striked text'),
             'insert':          '[i]{text}[/i]',
             'icon':            icon_url('strikethrough.png')},
            {'tagname':         'size',
             'name':            _('Font Size'),
             'description':     _('Change the font size'),
             'insert':          '[size={attr}]{text}[/size]',
             'values': [
                (8,             _('Tiny')),
                (11,            _('Small')),
                (13,            _('Normal')),
                (18,            _('Big')),
                (24,            _('Huge'))
             ]},
            {'tagname':         'color',
             'name':            _('Font Color'),
             'description':     _('Change Font Color'),
             'insert':          '[color={attr}]{text}[/color]',
             'values': [
                ('black',       _('Black')),
                ('blue',        _('Blue')),
                ('brown',       _('Brown')),
                ('cyan',        _('Cyan')),
                ('gray',        _('Gray')),
                ('green',       _('Green')),
                ('magenta',     _('Magenta')),
                ('purple',      _('Purple')),
                ('red',         _('Red')),
                ('white',       _('White')),
                ('yellow',      _('Yellow'))
             ]},
            {'tagname':         'url',
             'name':            _('Link'),
             'description':     _('Create a Link'),
             'icon':            icon_url('link.png'),
             'insert':          '[url]{text}[/url]'},
            {'tagname':         'img',
             'name':            _('Image'),
             'description':     _('Insert an image'),
             'icon':            icon_url('img.png'),
             'insert':          '[img]{text}[/img]'},
            {'tagname':         'code',
             'name':            _('Code'),
             'description':     _('Insert a codeblock'),
             'icon':            icon_url('code.png'),
             'insert':          '[code]{text}[/code]'},
            {'tagname':         'quote',
             'name':            _('Quote'),
             'description':     _('Insert a blockquote'),
             'icon':            icon_url('quote.png'),
             'insert':          '[quote]{text}[/quote]'}
        ]
