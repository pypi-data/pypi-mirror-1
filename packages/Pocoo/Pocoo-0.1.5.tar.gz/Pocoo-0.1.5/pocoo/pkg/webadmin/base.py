# -*- coding: utf-8 -*-
"""
    pocoo.pkg.webadmin.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo import Component
from pocoo.http import Response, TemplateResponse, PageNotFound, \
     AccessDeniedResponse
from pocoo.application import Page, LinkableMixin
from pocoo.template import PagePublisher


def get_sidebar(req, category, page):
    """
    Builds the sidebar.
    """
    is_index = not (category or page)
    _ = req.gettext
    categories = {}
    for comp in req.ctx.get_components(AdminCategory):
        categories[comp.identifier] = {
            'title':        comp.get_title(req),
            'description':  comp.get_description(req),
            'url':          comp.url,
            'identifier':   comp.identifier,
            'active':       comp.identifier == category,
            'pages':        []
        }
    for comp in req.ctx.get_components(AdminPage):
        category = categories[comp.category]
        category['pages'].append({
            'title':        comp.get_title(req),
            'description':  comp.get_description(req),
            'url':          comp.url,
            'identifier':   comp.identifier,
            'active':       comp.identifier == page
        })
    categories = categories.values()
    categories.sort(key=lambda x: x['title'].lower())
    for category in categories:
        category['pages'].sort(key=lambda x: x['title'].lower())
    return [{
        'title':            _('Overview'),
        'description':      _('Webadmin Overview'),
        'url':              req.ctx.make_url('admin/'),
        'identifier':       'index',
        'active':           is_index
    }] + categories + [{
        'title':            _('Back to the Forum'),
        'description':      _('Back to the Forum'),
        'url':              req.ctx.make_url(''),
        'identifier':       'forum',
        'active':           False
    }]


def get_category(req, category):
    for comp in req.ctx.get_components(AdminCategory):
        if comp.identifier == category:
            c = {
                'title':        comp.get_title(req),
                'description':  comp.get_description(req),
                'url':          comp.url,
                'identifier':   comp.identifier
            }
            pages = []
            for comp in req.ctx.get_components(AdminPage):
                if comp.category == category:
                    pages.append({
                        'title':        comp.get_title(req),
                        'description':  comp.get_description(req),
                        'url':          comp.url,
                        'identifier':   comp.identifier
                    })
            pages.sort(key=lambda x: x['title'].lower())
            c['pages'] = pages
            return c


class AdminCategory(Component, LinkableMixin):

    @property
    def identifier(self):
        return self.__class__.__name__

    @property
    def relative_url(self):
        return 'admin/%s/' % self.identifier

    def get_title(self, req):
        _ = req.gettext
        return _('Untitled')

    def get_description(self, req):
        _ = req.gettext
        return _('No Description')

    def get_index_page(self, req):
        pass


class AdminPage(Component, LinkableMixin):

    #: identifier of the category
    category = 'general'

    @property
    def identifier(self):
        return self.__class__.__name__

    @property
    def relative_url(self):
        return 'admin/%s/%s' % (self.category, self.identifier)

    def get_title(self, req):
        _ = req.gettext
        return _('Untitled')

    def get_description(self, req):
        _ = req.gettext
        return _('No Description')

    def get_admin_page(self, req):
        return PageNotFound()


class Webadmin(Page, PagePublisher):
    page_name = 'admin'
    relative_url = 'admin/'
    handler_regexes = [
        r'admin/$',
        r'admin/(?P<category>[^/]+)/$',
        r'admin/(?P<category>[^/]+)/(?P<page>[^/]+)$'
    ]

    def handle_request(self, req, category=None, page=None):
        if not req.user.acl.can_access_site('BOARD_ADMIN'):
            return AccessDeniedResponse()
        if category is None and page is None:
            template = 'webadmin/index.html'
            context = {}
        elif page is None:
            c = get_category(req, category)
            if c is None:
                return PageNotFound()
            template = 'webadmin/category.html'
            context = {
                'category':     c
            }
        else:
            for comp in self.ctx.get_components(AdminPage):
                if comp.identifier == page and \
                   comp.category == category:
                    rv = comp.get_admin_page(req)
                    if isinstance(rv, Response):
                        return rv
                    template, context = rv
                    break
            else:
                return PageNotFound()
        context['sidebar'] = get_sidebar(req, category, page)
        return TemplateResponse(template, **context)
