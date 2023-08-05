# -*- coding: utf-8 -*-
"""
    pocoo.pkg.webadmin.categories
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.pkg.webadmin.base import AdminCategory, get_category


class SettingsCategory(AdminCategory):
    identifier = 'settings'

    def get_title(self, req):
        _ = req.gettext
        return _('Settings')

    def get_description(self, req):
        _ = req.gettext
        return _('Allows you to change general settings like editing '
                 'the configuration, caching settings etc.')


class ForumCategory(AdminCategory):
    identifier = 'forum'

    def get_title(self, req):
        _ = req.gettext
        return _('Forum')

    def get_description(self, req):
        _ = req.gettext
        return _('Here you can configure the forums and categories')


class UserCategory(AdminCategory):
    identifier = 'user'

    def get_title(self, req):
        _ = req.gettext
        return _('User')

    def get_description(self, req):
        _ = req.gettext
        return _('Here you can edit users')
