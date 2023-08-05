# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.simplehtml
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides a MarkupFormat that allows the user to use
    HTML as markup but strips dangerous tags like ``<script>`` and others.

    It uses the ``secure_html`` method from the ``html`` util.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from pocoo.utils.html import secure_html
from pocoo.pkg.core.textfmt import MarkupFormat


class SimpleHTML(MarkupFormat):
    name = 'simplehtml'

    def parse(self, text):
        return secure_html(text)

    def quote_text(self, req, text, username=None):
        if username is not None:
            _ = req.gettext
            text = u'<em>%s:</em><br />%s' % ((_('%s wrote') % username), text)
        return u'<blockquote>%s</blockquote>' % text
