# -*- coding: utf-8 -*-
"""
    pocoo.utils.html
    ~~~~~~~~~~~~~~~~

    This module provides often used functions for handling html
    markup. Additionally there is a `SafeParser` that allows you
    to strip bad code like ``script`` tags and others.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
import string  # pylint: disable-msg=W0402
import htmlentitydefs
from HTMLParser import HTMLParser, HTMLParseError
from xml.sax.saxutils import quoteattr


#: Constants for regular expressions
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

word_split_re = re.compile(r'(\s+)')
hexcolor_re = re.compile(r'^\#[a-fA-F0-9]{3}([a-fA-F0-9]{3})?$')
punctuation_re = re.compile(
    '^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join(map(re.escape, LEADING_PUNCTUATION)),
     '|'.join(map(re.escape, TRAILING_PUNCTUATION))))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')


#: Defined HTML colors.
HTML_COLORS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}


def translate_color(color):
    """
    Translate a color name into a hex value or check
    if the given string is already a hex value.

    Raise ``ValueError`` if the argument isn't a valid color.
    """
    try:
        color = HTML_COLORS.get(color) or hexcolor_re.search(color).group()
    except AttributeError:
        raise ValueError('invalid color %r' % color)
    return color


def nl2br(text):
    """Automatically create <p> and <br> tags."""
    text = re.sub(ur'\r\n|\r|\n', u'\n', text)
    return u'\n\n'.join(u'<p>%s</p>' % p.replace(u'\n', u'<br />')
                        for p in re.split('\n{2,}', text))


def escape_html(text):
    """Escape &, <, > as well as single and double quotes for HTML."""
    if not isinstance(text, unicode):
        text = unicode(text)
    return text.replace(u'&', u'&amp;').  \
                replace(u'<', u'&lt;').   \
                replace(u'>', u'&gt;').   \
                replace(u'"', u'&quot;'). \
                replace(u"'", u'&#39;')


def unescape_html(text):
    """Unescape &, <, > as well as single and double quotes from HTML."""
    return text.replace(u'&#39;', u"'").  \
                replace(u'&quot;', u'"'). \
                replace(u'&gt;', u'>').   \
                replace(u'&lt;', u'<').   \
                replace(u'&amp;', u'&')


def urlize(text, trim_limit=None, nofollow=False):
    """
    Convert any URLs in text into clickable links. Works on http://, https:// and
    www. links. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right thing.

    If ``trim_limit`` is not ``None``, the URLs in link text will be limited to
    ``trim_limit`` characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.
    """
    def trim_url(x):
        if trim_limit:
            return x[:trim_limit] + (len(x) >= trim_limit and '...' or '')
        else:
            return x

    nofollow_attr = nofollow and ' rel="nofollow"' or ''

    words = word_split_re.split(text)
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or (
                middle and not middle.startswith('http://') and
                '@' not in middle and
                middle[0] in string.letters + string.digits and (
                    middle.endswith('.org') or
                    middle.endswith('.net') or
                    middle.endswith('.com')
                )
            ):
                middle = u'<a href="http://%s"%s>%s</a>' % \
                         (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = u'<a href="%s"%s>%s</a>' % \
                         (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and \
               ':' not in middle and \
               simple_email_re.match(middle):
                middle = u'<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)


class SafeParser(HTMLParser):
    """
    A HTMLParser subclass that strips dangerous tags.
    """

    DEPRECATED = {
        'b':        ('strong', None),
        'i':        ('em', None),
        'u':        ('ins', None),
        's':        ('del', None),
        'center':   ('span', 'text-align: center'),
        'big':      ('span', 'font-size: x-large'),
        'small':    ('span', 'font-size: x-small'),
        'strike':   ('del', None),
        'font':     ('span', None)
    }
    ALLOWED = ('a', 'abbr', 'acronym', 'address', 'applet', 'area', 'b',
               'big', 'blockquote' 'br', 'button', 'caption', 'center',
               'cite', 'code', 'dd', 'del', 'dfn', 'div', 'dl', 'dt',
               'em', 'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
               'i', 'img', 'ins', 'label', 'legend', 'li', 'map',
               'ol', 'p', 'param', 'pre', 'q', 's', 'samp', 'small',
               'strike', 'strong', 'sub', 'sup', 'table', 'tbody',
               'td', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var')
    INLINE = ('img', 'br', 'hr')

    font_face_re = re.compile('^[a-zA-Z,\s]+$')
    font_size_re = re.compile('^[+-]?[0-7]+$')

    def __init__(self):
        self._result = []
        self._opened = []
        self._lock = []
        HTMLParser.__init__(self)

    def _write_tag(self, name, attributes, close=False):
        tmp = []
        for key, value in attributes.iteritems():
            tmp.append(u'%s=%s' % (key, quoteattr(value)))
        attributes = u''
        if tmp:
            attributes = u' ' + u' '.join(tmp)
        close = close and u' /' or u''
        self._result.append(u'<%s%s%s>' % (name, attributes, close))
        if not close:
            self._opened.append(name)

    def _close_tag(self, name):
        last_tag = None
        while last_tag != name:
            if not self._opened:
                return
            last_tag = self._opened.pop()
            self._result.append(u'</%s>' % last_tag)

    def _write_data(self, data):
        self._result.append(escape_html(data))

    def _rewrite_font(self, attrs):
        face = attrs.pop('face', None)
        size = attrs.pop('size', None)
        color = attrs.pop('color', None)
        tmp = []

        if face is not None and self.font_face_re.search(face) is not None:
            parts = []
            for p in face.split(','):
                parts.append('\'%s\'' % p.strip())
            tmp.append(u'font-family: %s' % u', '.join(parts))

        if size is not None and self.font_size_re.search(size) is not None:
            if size[0] in ('+', '-'):
                size = size[1:]
            size = int(size)
            tmp.append(u'font-size: %dpt' % (size * 3.8))

        if color is not None:
            try:
                tmp.append(u'color: %s' % translate_color(color))
            except ValueError:
                pass

        style = u'; '.join(tmp)
        if style:
            attrs['style'] = style

    def handle_starttag(self, tag, attrs):
        # dangerous tags
        if tag not in self.ALLOWED:
            if not self._lock:
                self._lock[:] = (tag,)
                return

        # check attributes
        attrs = dict((name, value) for name, value in attrs if
                     not name.startswith('on') and name != 'style')

        # handle font
        if tag == 'font':
            tag = 'span'
            self._rewrite_font(attrs)

        # handle deprecated tags
        elif tag in self.DEPRECATED:
            tag, style = self.DEPRECATED[tag]
            if style:
                attrs['style'] = style

        if not self._lock:
            self._write_tag(tag, attrs, tag in self.INLINE)

    def handle_endtag(self, tag):
        if self._lock:
            if self._lock[-1] == tag:
                self._lock.pop()
        if not self._lock:
            self._close_tag(self.DEPRECATED.get(tag, (tag,))[0])

    def handle_startendtag(self, tag, attrs):
        if tag in self.INLINE:
            self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self._lock:
            return
        self._write_data(data)

    def handle_charref(self, ref):
        try:
            self._write_data(unichr(int(ref)))
        except (TypeError, ValueError):
            pass

    def handle_entityref(self, name):
        try:
            self._write_data(unichr(htmlentitydefs.name2codepoint[name]))
        except (KeyError, TypeError):
            pass

    def get_output(self):
        return u''.join(self._result)

    def close(self):
        self._close_tag(True)
        HTMLParser.close(self)


def secure_html(text):
    """
    Return a safe version of a given html code.
    """
    try:
        parser = SafeParser()
        parser.feed(text)
        parser.close()
    except HTMLParseError:
        return escape_html(text)
    return parser.get_output()
