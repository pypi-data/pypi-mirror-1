# -*- coding: utf-8 -*-
"""
    pocoo.template
    ~~~~~~~~~~~~~~

    Pocoo templating, using the *Jinja* template engine.

    Basic usage::

        from pocoo.template import Template

        context = {'forum': {'id': 23, 'name': 'blub blub'}}
        Template(req, 'viewforum').render(context)

    You can use the special response class `pocoo.http.TemplateResponse`
    to render a template to a new response.


    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import os
import cPickle as pickle
import md5
import time

import jinja
import jinja.base
import jinja.exceptions

from pocoo import Component
from pocoo.application import LinkableMixin
from pocoo.settings import cfg
from pocoo.exceptions import MissingResource
from pocoo.utils.debug import dtk


class PagePublisher(Component, LinkableMixin):
    """
    Automatically publishes the page object on
    ``pages.PageName`` until you overwrite `page_name`.

    Pages inheriting from this component automatically provide
    link methods like models and appear in the global template
    context.
    """

    @property
    def page_name(self):
        return self.__class__.__name__
    relative_url = page_name


class TemplateContextModifier(Component):
    """Allows a component to register superglobal context variables."""

    def modify_context(self, req, context):
        """get passed the context to modify it in place."""


class PocooLoader(object):
    """
    Custom loader for Pocoo templates.
    Searches the instance template path as given in the config, then
    the template providers (which, for example, load templates shipped
    in packages), and at last the templates shipped with Pocoo.
    """
    memcache = cfg.bool('cache', 'template_memcache', False)
    diskcache = cfg.bool('cache', 'template_diskcache', False)

    def __init__(self, ctx):
        self.ctx = ctx
        self.cachescheme = os.path.join(ctx.cfg.root, 'cache', '%s.template')

    def load(self, name, parent=None):
        if '::' in name:
            basename, name = name.split('::', 1)
        elif parent is not None and '::' in parent:
            basename = parent.split('::', 1)[0]
        else:
            basename = 'default'
        try:
            return unicode(self.ctx.pkgmanager.get_resource('templates',
                           basename, name, 'site'), 'utf-8')
        except MissingResource, e:
            raise jinja.exceptions.TemplateDoesNotExist(e.args[0])
        except UnicodeError, e:
            raise jinja.exceptions.TemplateCharsetError('Pocoo template must '
                                                        'be encoded in utf-8', e)

    def _get_nodelist(self, name, lib, parent):
        """
        Helper to avoid code duplication in load_and_compile.
        """
        template = self.load(name, parent)
        lexer = jinja.base.Lexer(template)
        parser = jinja.base.Parser(lexer.tokenize(), self, lib, name)
        return parser.parse()

    def load_and_compile(self, name, lib=None, parent=None):
        put_into_memcache = False
        if self.memcache:
            mem_cache_name = 'template/%s' % name
            if mem_cache_name in self.ctx._cache:
                return self.ctx._cache[mem_cache_name]
            put_into_memcache = True
        if self.diskcache:
            disk_cache_name = self.cachescheme % md5.new(name).hexdigest()
            if not os.path.exists(disk_cache_name):
                nodelist = self._get_nodelist(name, lib, parent)
                try:
                    pickle.dump(nodelist, file(disk_cache_name, 'wb'),
                                protocol=2)
                except IOError:
                    pass
            else:
                try:
                    nodelist = pickle.load(file(disk_cache_name, 'rb'))
                except IOError:
                    nodelist = self._get_nodelist(name, lib, parent)
        nodelist = self._get_nodelist(name, lib, parent)
        if put_into_memcache:
            self.ctx._cache[mem_cache_name] = nodelist
        return nodelist

    def load_and_compile_uncached(self, name, lib=None, parent=None):
        return self._get_nodelist(name, lib, parent=None)


def render_template(req, name, context):
    """
    Render a template called name with the preliminary
    context. Adds a couple of system variables to the context.

    TODO: cache system context
    """
    t_1 = time.time()
    ctx = req.ctx
    addvars = {
        'cobalt':   '%s!cobalt' % req.ctx.scriptname
    }
    syscontext = {
        # XXX: necessary?
        'REQUEST':          req,
        'pages':            {},
        'system': {
            'template':     addvars,
            'pocoo': { # FIXME: from somewhere, but definitively not here
                'expose':   True,
                'url':      'http://www.pocoo.org/'
            },
            'conf':         ctx.cfg.to_dict()
        },
        'base_url':         req.ctx.make_external_url(""),
        'user':             req.user
    }
    for page in ctx.get_components(PagePublisher):
        syscontext['pages'][page.page_name] = page

    # fetch data from context modifiers
    for modifier in req.ctx.get_components(TemplateContextModifier):
        modifier.modify_context(req, syscontext)

    context.update(syscontext)
    c = jinja.Context(context)

    template_name = req.user.settings.get('template', 'default')
    nodelist = req.ctx.template_loader.load_and_compile(
        '%s::%s' % (template_name, name),
        req.ctx._template_lib
    )
    ret = nodelist.render(c)

    t_2 = time.time()
    dtk.log('template', 'rendered %r in %0.5f sec', name, t_2 - t_1)

    return ret
