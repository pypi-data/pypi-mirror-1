# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.i18n
    ~~~~~~~~~~~~~~~~~~~

    Pocoo internationalization components.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import gettext
from pocoo.application import RequestWrapper
from jinja.nodes import Node, KeywordNode, VariableNode, ValueNode, CollectionNode
from jinja.base import TOKEN_TEXT, TOKEN_VAR
from jinja.exceptions import TemplateSyntaxError
from cStringIO import StringIO


class TranslatableTag(Node):
    """
    Translatable Tag
    ================

    Usage::

        {% trans %}
        somestring
        {% trans %}

    Or::

        {% trans "string" %}
    """

    rules = {
        'long': [KeywordNode('trans')],
        'plural': [KeywordNode('trans'), KeywordNode('pluralizing'),
                   VariableNode()],
        'short': [KeywordNode('trans'), ValueNode(), CollectionNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        self._body_pl = []
        self._vars_pl = {}
        if matched_tag == 'short':
            self._body_sg = [handler_args[1].resolve()]
            self._vars_sg = handler_args[2]
        else:
            self._body_sg, self._vars_sg, self._body_pl, self._vars_pl = \
                self._forkparse(parser)
        if matched_tag == 'plural':
            self._indicator = handler_args[2]
        self.msgid = (''.join(self._body_sg)).strip()
        self.msgid_plural = (''.join(self._body_pl)).strip()
        Node.__init__(self)

    def _forkparse(self, parser):
        lib = parser.library
        sg = []; vars_sg = {}
        pl = []; vars_pl = {}
        out = sg; vars_out = vars_sg
        while parser.tokens:
            token = parser.pop_token()
            if token.token_type == TOKEN_VAR:
                var = lib.parse(parser, u'print %s' % token.contents)
                var_key = token.contents.split('|')[0].strip()
                vars_out[var_key] = var
                out.append('%%(%s)s' % var_key)
            elif token.token_type == TOKEN_TEXT:
                lines = token.contents.splitlines()
                # XXX: this protects whitespaces between different tokens (really?)
                text = u'\n'.join(lines[:1] + [line.lstrip() for line in lines[1:]])
                out.append(text)
            else:
                if token.contents == 'plural':
                    if out is sg:
                        out = pl
                        vars_out = vars_pl
                    else:
                        raise TemplateSyntaxError('plural used twice')
                elif token.contents == 'endtrans':
                    break
                else:
                    raise TemplateSyntaxError('you can\'t use blocks inside of a '
                                              '`trans` tag.')
        return sg, vars_sg, pl, vars_pl

    def render(self, context):
        req = context['REQUEST']
        if self.msgid_plural:
            var = 1
            if hasattr(self, '_indicator'):
                var = self._indicator.resolve(context)
            rv = req.gettext(self.msgid, self.msgid_plural, var)
        else:
            rv = req.gettext(self.msgid)
        if isinstance(self._vars_sg, list):
            return rv % tuple(v.render(context) for v in self._vars_sg)
        args = dict((n, v.render(context)) for n, v in self._vars_sg.iteritems())
        args.update(self._vars_pl)
        return rv % args


def load_translations(ctx, lng):
    """
    loads all available translations for the given language.
    """
    result = []
    for res in ctx.pkgmanager.get_resources('i18n', '', lng):
        f = StringIO(res)
        result.append(gettext.GNUTranslations(f))
    return result


def parse_http_accept_language(s):
    """
    Return the accepted languages as set in the user browser.
    """
    result = []
    for item in s.split(','):
        lng = item.split(';', 1)[0]
        lng = lng.lower()
        result.append(lng)
        if '-' in lng:
            result.append(lng.split('-')[0])
    return result


def get_request_languages(req):
    """
    Return the list of languages a request could handle.
    """
    if hasattr(req, 'user') and req.user is not None \
       and req.user.language:
        lng = [req.user.language]
    else:
        lng = []
    # before checking the HTTP_ACCEPT_LANGUAGE check for
    # a forced language.
    forced = req.ctx.cfg.get('general', 'language', '')
    if forced and forced != 'auto' and forced not in lng:
        lng.append(forced)
    # now prase the HTTP_ACCEPT_LANGUAGE string and add
    # the languages to the list of accepted languages.
    language_string = req.environ.get('HTTP_ACCEPT_LANGUAGE', 'en')
    for item in parse_http_accept_language(language_string):
        if item not in lng:
            lng.append(item)
    # add "en" if not set
    if 'en' not in lng:
        lng.append('en')
    return lng


class Translator(object):
    """
    A callable that allows you to use pluralized and
    non pluralized strings. A translator instance always
    exists on the request object as ``req.gettext``::

        _ = req.gettext
        _('Hello World!', 'Hello Worlds!', 2)

    The example above defines a singular and pluralized
    version of "Hello World". The number two tells the
    gettext system that we have two worlds in that case.
    Some languages provide more than just one plural form
    so this number allows it to decide which plural form
    to use.

    If you just have a singular string you can use this::

        _ = req.gettext
        _('This is just a small example')

    Strings marked as ``_()`` automagically get tracked
    by the gettext translation generator script.
    """

    def __init__(self, translations, languages):
        #XXX: should we cache that?
        self.translator = gettext.NullTranslations()
        for lng in languages:
            for translation in translations[lng]:
                self.translator.add_fallback(translation)
        self.languages = languages

    def __call__(self, msg, plural=None, n=1):
        if plural is None:
            return self.translator.ugettext(msg)
        return self.translator.ungettext(msg, plural, n)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.languages
        )


dummy_translate = Translator({}, [])


class I18nWrapper(RequestWrapper):

    def __init__(self, ctx):
        super(I18nWrapper, self).__init__(ctx)
        self.translations = {}

    def get_priority(self):
        return 4

    def process_request(self, req):
        """Attach a gettext and dummy translate method to the request."""
        languages = get_request_languages(req)
        req.accept_languages = languages
        for lng in languages:
            if lng not in self.translations:
                self.translations[lng] = load_translations(self.ctx, lng)
        req.gettext = Translator(self.translations, languages)
        req.dummy_translate = dummy_translate

    def process_response(self, req, resp):
        return resp
