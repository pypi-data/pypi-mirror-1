# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.smilies
    ~~~~~~~~~~~~~~~~~~~~~~

    Pocoo smilies parser.

    :copyright: 2006 by Benjamin Wiegand, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo import Component
from pocoo.utils.html import escape_html


def replace_smilies(ctx, text):
    """
    Replace smilies in ``text``, using all providers listed in the
    board config.
    """
    smiley_providers = ctx.cfg.get('board', 'smiley_providers', ['default'])
    for provider in ctx.get_components(SmileyProvider):
        if provider.name not in smiley_providers:
            continue
        for smiley in provider.smilies:
            text = text.replace(smiley[0], provider.render_smiley(smiley))
    return text


def get_smiley_buttons(ctx):
    """
    Return a list of button dictionaries usable for the BBCodeEditor
    JavaScript app.
    """
    res = []
    smiley_providers = ctx.cfg.get('board', 'smiley_providers', ['default'])
    for provider in ctx.get_components(SmileyProvider):
        if provider.name not in smiley_providers:
            continue
        for smiley in provider.smilies:
            res.append(smiley + (ctx.make_url(provider.smiley_dir),))
    return res


class SmileyProvider(Component):
    """
    A SmileyProvider maps small text strings to images.
    """

    #: List of smilies this component provides, in the form
    #: ``('textform', 'imagename')``.
    #: ``imagename`` is relative to the ``smiley_dir`` below.
    smilies = []

    #: Directory where smilies of this provider can be found.
    #: Must be relative to the forum root, e.g.
    #: ``!cobalt/pkgname/default/img/smilies/``.
    smiley_dir = ""

    #: Name (can be overwritten, must be lowercase).
    #: Used for the configuration setting.
    @property
    def name(self):
        return self.__class__.__name__.lower()

    def render_smiley(self, smiley):
        """
        Render a smiley. This doesn't need to be overridden in normal
        cases.

        :return: HTML for the smiley image.
        """
        return '<img src="%s" alt="%s" />' % (
            self.ctx.make_url(self.smiley_dir, smiley[1]),
            escape_html(smiley[0])
        )


class Default(SmileyProvider):
    """
    Default Pocoo smilies.
    """
    smilies = [
        (';-)', 'wink.png'),
        (':(',  'sad.png'),
        (':-)', 'smile.png'),
        (':D',  'grin.png'),
    ]

    smiley_dir = '!cobalt/core/default/img/smilies/'
