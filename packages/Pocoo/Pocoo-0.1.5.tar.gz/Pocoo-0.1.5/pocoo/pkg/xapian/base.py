# -*- coding: utf-8 -*-
"""
    pocoo.pkg.xapian.base
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Christoph Hack.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.application import Page, LinkableMixin
from pocoo.http import Response, TemplateResponse
from pocoo.template import PagePublisher
from pocoo.utils.form import Form, TextField
from pocoo.utils.validators import isNotEmpty
from pocoo.db import meta
from pocoo.pkg.core import db

from index import Index

class XapianSearchHandler(Page, PagePublisher, LinkableMixin):
    page_name = 'search'
    relative_url = 'search/'
    handler_regexes = [
        r'search/$'
    ]

    def handle_request(self, req):
        form = Form(req, self, 'POST',
            TextField('keywords',
                validator=isNotEmpty()
            )
        )
        if req.method == 'POST':
            form.update(req.form, prefix='s_')
            if not form.has_errors:
                idx = Index(req.ctx)
                qry = form.to_dict()['keywords']
                posts = idx.search(req, str(qry))
                print posts
                context = {
                    'threads': posts,
                    'query': qry
                }
                return TemplateResponse('results.html', **context)

        context = {
            'form': form.generate(prefix='s_')
        }
        return TemplateResponse('search.html', **context)
