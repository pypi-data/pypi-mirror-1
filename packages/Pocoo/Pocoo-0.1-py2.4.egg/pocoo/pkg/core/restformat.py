# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.restformat
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Pocoo ReST Parser.

    A thin wrapper around the docutils ReST parser.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

from pocoo.pkg.core.textfmt import MarkupFormat
from pocoo.utils.html import escape_html
from pocoo.pkg.core.smilies import replace_smilies


class ReST(MarkupFormat):
    """
    ReST markup format.
    """

    name = 'rest'

    def parse(self, text, signature):
        from docutils.core import publish_parts

        try:
            parts = publish_parts(source=text, writer_name='html4css1')
            text = parts['fragment'].strip()
        except Exception:
            # TODO: figure out which exceptions this can raise
            text = escape_html(text).strip()
        #XXX: render smilies just in text blocks
        return replace_smilies(self.ctx, text)

    def quote_text(self, req, text, username=None):
        lines = [u'    %s' % line for line in text.splitlines()]
        if username is not None:
            _ = req.gettext
            lines.insert(0, (u'    **%s**:' % _('%s wrote')) % username)
        return u'\n'.join(lines)
