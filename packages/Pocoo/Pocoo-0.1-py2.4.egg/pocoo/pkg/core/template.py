# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.template
    ~~~~~~~~~~~~~~~~~~~~~~~

    Templating helpers.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import math
import jinja.exceptions
from jinja.nodes import Node, KeywordNode, VariableNode, CollectionNode


class Pagination(object):
    """
    Pagination Controller. Push this into the template so that
    the template designer has an object he can use for generating
    an pagination.

    Normally you are looking for the ``LazyPagination`` class, this
    one is just for posts or if you have many single items which
    are combined to a thread etc. The idea is that you don't have
    and offset information in the url.
    """

    def __init__(self, req, idlist, start, per_page, link):
        """
        :param req:      the request
        :param idlist:   a list of all ids for the pagination
        :param start:    the position of the first item on the page
        :param per_page: number of items on each page
        :param link:     function which takes one id and returns a link for it

        Example::

            p = Pagination(req, range(50), 20, 20, lambda x: 'post/%d' % x)

        In this example the first page would contain the posts 0-19,
        the second 20-39 and the first 40-50.
        """
        self.req = req
        self.idlist = idlist
        self.start = start
        self.per_page = per_page
        self.link = link

    def generate(self, normal, active, commata, ellipsis, threshold):
        """
        Generate a Pagination of the data defined in the constructor.

        :param normal:    inserted string when the page isn't active
        :param active:    inserted string when the page is active
        :param commata:   inserted between links
        :param ellipsis:  inserted as space indicator for skiped links
        :param threshold: number of links around start/current page and
                          end before they will be replaced by an ellipsis

        ``normal`` and ``active`` can contain out of the following formatting
        chars:

        ======================  ==================================
        ``%(page)s``            number of the current page
        ``%(url)s``             absolute url of the current page
        ======================  ==================================

        Example::

            p.generate('<a href="%(url)s">%(page)s</a>',
                       '<strong>%(page)s</strong>',
                       ', ',
                       ' ... ',
                       3)
        """
        current_page_number = self.start / self.per_page + 1
        number_of_pages = int(math.ceil(len(self.idlist) / (self.per_page * 1.0)))
        was_space = False
        result = []
        for idx in range(1, number_of_pages + 1):
            if idx <= threshold or idx > number_of_pages - threshold or\
               abs(current_page_number - idx) < math.ceil(threshold / 2.0):
                if result and result[-1] != ellipsis:
                    result.append(commata)
                was_space = False
                if idx == current_page_number:
                    schema = active
                else:
                    schema = normal
                url = self.link(self.idlist[(idx - 1) * self.per_page])
                result.append(schema % {
                    'page': idx,
                    'url':  self.req.ctx.make_url(url),
                })
            else:
                if not was_space:
                    was_space = True
                    result.append(ellipsis)
        return u''.join(result)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            str(self)
        )

    def __str__(self):
        return self.generate('%(page)s', '[%(page)s]', ', ', ' ... ', 3)


class LazyPagination(object):
    """
    A lazy pagination controller. Doesn't require a id list like
    the ``Pagination`` controller.

    The ``LazyPagination`` is a cheep to calculate pagination based
    on the current page, the total amount of pages and the information
    about what a link looks like and how many items you have per page.
    """

    def __init__(self, req, page, per_page, pages, link):
        self.req = req
        self.page = page
        self.per_page = per_page
        self.pages = pages
        self.link = link

    def generate(self, normal, active, commata, ellipsis, threshold):
        """
        Generate a Pagination of the data defined in the constructor.

        :param normal:    inserted string when the page isn't active
        :param active:    inserted string when the page is active
        :param commata:   inserted between links
        :param ellipsis:  inserted as space indicator for skiped links
        :param threshold: number of links around start/current page and
                          end before they will be replaced by an ellipsis

        ``normal`` and ``active`` can contain out of the following formatting
        chars:

        ======================  ==================================
        ``%(page)s``            number of the current page
        ``%(url)s``             absolute url of the current page
        ======================  ==================================

        Example::

            p.generate('<a href="%(url)s">%(page)s</a>',
                       '<strong>%(page)s</strong>',
                       ', ',
                       ' ... ',
                       3)
        """
        was_space = False
        result = []
        for idx in range(1, self.pages + 1):
            if idx <= threshold or idx > self.pages - threshold or\
               abs(self.page - idx) < math.ceil(threshold / 2.0):
                if result and result[-1] != ellipsis:
                    result.append(commata)
                was_space = False
                if idx == self.page:
                    schema = active
                else:
                    schema = normal
                url = self.link(idx)
                result.append(schema % {
                    'page': idx,
                    'url':  self.req.ctx.make_url(url),
                })
            else:
                if not was_space:
                    was_space = True
                    result.append(ellipsis)
        return u''.join(result)

    def __str__(self):
        return self.generate('%(page)s', '[%(page)s]', ', ', ' ... ', 3)


class PaginationTag(Node):
    """
    Generates a pagination. requires a Pagination object at first
    argument::

        {% paginate forum.pagination
            '<a href="%(link)s">%(page)s</a>',
            '<strong>%(page)s</strong>',
            ', ',
            '...'
         %}
    """
    rules = {
        'default':  [KeywordNode('paginate'), VariableNode(),
                     CollectionNode()]
    }
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._variable = handler_args[1]
        self._arguments = handler_args[2]
        Node.__init__(self)

    def render(self, context):
        pagination_controller = self._variable.resolve(context)
        if len(self._arguments) < 4:
            raise jinja.exceptions.TemplateRuntimeError('invalid argument count '
                                                        'for {% paginate %}')
        link_scheme = self._arguments[0].resolve(context)
        active_scheme = self._arguments[1].resolve(context)
        commata = self._arguments[2].resolve(context)
        ellipsis = self._arguments[3].resolve(context)
        if len(self._arguments) == 5:
            threshold = self._arguments[4].resolve(context)
        else:
            threshold = 3
        return pagination_controller.generate(link_scheme, active_scheme,
                                              commata, ellipsis, threshold)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
