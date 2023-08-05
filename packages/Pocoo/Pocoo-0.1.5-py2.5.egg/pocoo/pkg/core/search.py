# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.search
    ~~~~~~~~~~~~~~~~~~~~~

    Pocoo Search System

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
from math import ceil
from pocoo import Component
from pocoo.application import LinkableMixin
from pocoo.pkg.core.template import LazyPagination


_highlight_re = re.compile(r'(?<!\\)!(.*?)(?<!\\)!')


class Result(LinkableMixin):
    """
    Search result object.
    """

    def __init__(self, title, relative_url, description, fresh=False):
        """
        :Parameters:
          `title`: The title for the search page. Usually that's
            the clickable part.

          `relative_url`: The relative url of the found page. If the
            page is not part of this pocoo installation (for example
            an external link to a wiki etc.) the link must be a
            full canonical link with scheme, hostname port etc.

          `description`: A short description of the found page. This
            must not include html markup or any other markup. But it's
            possible to highlight words in it. If you want a word
            highlighted wrap it with exclamation marks::

                This is the description of the text with !some
                highlighted words!.

            Because of this exclamation marks in the text must be
            escaped with a backslash.

          `fresh`: Boolean value that indicates this result as fresh.
            A fresh positing is highlighted on the result page. This
            for example can mean "unread" post or "recent change" etc.
        """
        self.title = title
        self.relative_url = relative_url
        self.description = description
        self.fresh = fresh

    @property
    def rendered_description(self):
        """HTML version of the description with highlighted parts
        wrapped with ``<span class="highlight">``."""
        result = _highlight_re.sub(u'<span class="highlight">\\1</span>',
                                   self.description)
        return result.replace(u'\\!', u'!')

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.title
        )


class SearchEngine(Component):
    #: name of this search engine
    name = None

    def search(self, acl, rule, per_page, page):
        """Start a search for `rule`. This method has to return
        the search results for the page `page` where `per_page`
        items should be visible for each page.

        The return value must be a tuple in the form
        ``(number_of_matches, matches)`` where `number_of_matches`
        is the number of total matches, and `matches` an iterable
        of `Result` objects for only this page.

        The search function must check the returned data against
        the acl object."""
        return 0, ()


def get_search_engine(ctx):
    """Return the active search engine or raise a `ValueError`
    if search engine is not found."""
    search_engine = ctx.cfg.get('search', 'engine', 'none')
    for comp in ctx.get_components(SearchEngine):
        if comp.name == search_engine:
            return comp
    raise ValueError('search engine not found')


def search(req, rule, per_page, page):
    """Start a search query and return a tmeplate
    context."""
    if not req.ctx.get_bool('search', 'enabled', False):
        return
    try:
        engine = get_search_engine(req.ctx)
    except ValueError:
        return
    rv = engine.search(req.user.acl, rule, per_page, page)
    results = list(rv[1])
    if not results:
        return

    def get_page_link(number):
        link = 'search/'
        if number > 1:
            link += '?page=%d' % number
        return link

    page_count = int(ceil(rv[0] / float(per_page)))
    pagination = LazyPagination(req, page, per_page,
                                page_count, get_page_link)
    return {
        'results':      results,
        'pagination':   pagination
    }
