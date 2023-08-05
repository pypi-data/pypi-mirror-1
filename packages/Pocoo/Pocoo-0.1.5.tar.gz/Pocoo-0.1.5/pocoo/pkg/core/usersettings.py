# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.usersettings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User Settings support.

    :copyright: 2006 by Armin Ronacher, Lukas Meuser.
    :license: GNU GPL, see LICENSE for more details.
"""
import os
from os import path
from pocoo import Component
from pocoo.http import PageNotFound, HttpRedirect
from pocoo.application import LinkableMixin
from pocoo.utils.image import resize_image
from pocoo.utils.uri import urlencode
from pocoo.pkg.core.textfmt import get_editor
from pocoo.pkg.core.forms import UserSignatureForm, UserProfileForm, \
     AvatarForm, UserForumSettingsForm
from pocoo.utils.tabbox import TabBox, Tab
from pocoo.pkg.core.remotecall import RemoteCallable, export
from pocoo.pkg.core.textfmt import parse_and_render
from pocoo.template import render_template


class UserSettingsPage(Component, LinkableMixin):

    @property
    def settings_page_identifier(self):
        """The name of the page which is also the url
        under which the page will be visible::

            /settings/$SETTINGS_PAGE_IDENTIFIER$"""
        return self.__class__.__name__

    @property
    def relative_url(self):
        return 'settings/%s' % self.settings_page_identifier

    def get_settings_link_title(self, req):
        """Has to return a text for the link title in the
        settings sidebar (this musn't be a sidebar, in fact
        it depends on the template.

        If the method returns ``None`` the template wont
        render this link."""

    def get_settings_page(self, req):
        """This method automatically gets called when a
        user requests this settings page. It must either
        return a valid Response object or a tuple in the
        form (template, context) where template is a string
        with the template filename and context is a dict
        which automatically gets updated with the generated
        sidebar so that templates can access it."""



class UserSignatureSettings(UserSettingsPage, RemoteCallable):
    """
    This page allows the user to create / edit his signature
    using an editor.
    """
    settings_page_identifier = 'signature'

    @export('settings.signature.box')
    def box(self, req, page, *args):
        page = int(page)
        if page == 0:
            return render_template(req, 'partial/preview.html', {
                'text': parse_and_render(req, len(args) and args[0] or "", \
                        signature=True)
            })

    def get_settings_link_title(self, req):
        _ = req.gettext
        return _('Signature')

    def get_settings_page(self, req):
        _ = req.gettext
        msg = None

        form = UserSignatureForm(req, self, 'POST', {
            'signature': req.user.profile.get('signature', u'')
        })

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                req.user.profile.update(form.to_dict())
                req.user.save()
                msg = _('Signature saved')

        f = form.generate(prefix='f_')

        box = TabBox(req, self.box, True,
            Tab(_("Preview"), static=False, send=[f["signature"]["name"]],
                short_name="preview")
        )

        js, options = get_editor(req, signature=True)
        return 'settings/signature.html', {
            'form':             f,
            'msg':              msg,
            'editor_options':   options,
            'editor_javascript':js,
            'tabbox':           box
        }


class UserProfileSettings(UserSettingsPage):
    """
    This page allows the user to edit his public information.

    XXX: make this more flexible -- later (LATER!!!!)
    """
    settings_page_identifier = 'profile'

    def get_settings_link_title(self, req):
        _ = req.gettext
        return _('Profile')

    def get_settings_page(self, req):
        _ = req.gettext
        get_setting = lambda x: req.user.profile.get(x, u'')
        msg = None

        form = UserProfileForm(req, self, 'POST', {
            'email':        req.user.email,
            'show_email':   req.user.settings.get('show_email') or False,
            'aol':          get_setting('aol'),
            'icq':          get_setting('icq'),
            'jabber':       get_setting('jabber'),
            'msn':          get_setting('msn'),
            'yahoo':        get_setting('yahoo'),
            'website':      get_setting('website'),
            'location':     get_setting('location'),
            'interests':    get_setting('interests')
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                # set special setting values
                if d['new_password']:
                    req.user.set_password(d.pop('new_password'))
                else:
                    del d['new_password']
                del d['new_password2']
                req.user.email = d.pop('email')
                req.user.settings.update({'show_email': d.pop('show_email')})
                # update other profile fields
                req.user.profile.update(d)
                req.user.save()
                msg = _('Settings saved')
        return 'settings/profile.html', {
            'form':         form.generate(prefix='f_'),
            'msg':          msg
        }


class AvatarSettings(UserSettingsPage):
    """
    This page allows the user to update his avatar
    """
    settings_page_identifier = 'avatar'

    def get_settings_link_title(self, req):
        if req.ctx.cfg.get_bool('board', 'allow_avatars', True):
            _ = req.gettext
            return _('Avatar')

    def get_settings_page(self, req):
        if not req.ctx.cfg.get_bool('board', 'allow_avatars', True):
            return PageNotFound()
        _ = req.gettext
        msg = None

        def make_small_thumbnail(value):
            if not value:
                return
            dim = self.ctx.cfg.get_int('board', 'avatar_dimension', 80)
            return resize_image(value, dim, dim, 'image/png')

        form = AvatarForm(req, self, 'POST')
        avatar = None
        if req.method == 'POST':
            form.update(req.files, prefix='f_')
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                uid = req.user.user_id
                fn = path.join(self.ctx.cfg.root, 'avatars', '%d.png' % uid)
                if d['delete_avatar']:
                    req.user.profile['avatar'] = None
                    if path.exists(fn):
                        os.unlink(fn)
                elif d['avatar']:
                    uid = req.user.user_id
                    f = file(fn, 'wb')
                    f.write(d['avatar'])
                    f.close()
                    req.user.profile['avatar'] = self.ctx.make_url(
                        'users', urlencode(req.user.username), show='avatar')
                req.user.save()
                msg = _('Settings saved')
        # TODO: support for linked avatars and gravatars
        elif req.user.profile.get('avatar'):
            avatar = self.ctx.make_url('users', urlencode(req.user.username),
                                       show='avatar')
        return 'settings/avatar.html', {
            'form':     form.generate(prefix='f_'),
            'avatar':   avatar,
            'msg':      msg
        }


class UserForumSettings(UserSettingsPage):
    """
    This page allows the user to update his forum view settings
    (ie. view mode and posts and threads per page)
    """

    settings_page_identifier = 'forum'

    def get_settings_link_title(self, req):
        _ = req.gettext
        return _('Forum Settings')

    def get_settings_page(self, req):
        def int_or_none(x):
            "manipulator which returns an int or None"
            try:
                return int(x)
            except ValueError:
                return None

        _ = req.gettext
        msg = None

        form = UserForumSettingsForm(req, self, 'POST', {
            'posts_per_page':   req.user.settings.get('posts_per_page') or '',
            'threads_per_page': req.user.settings.get('threads_per_page') or '',
            'view_mode':        req.user.settings.get('view_mode') or '',
            'ajax':             req.user.settings.get('ajax')
        })

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                req.user.settings.update(d)
                req.user.save()
                msg = _('Forum settings saved')

        return 'settings/forumsettings.html', {
            'form':         form.generate(prefix='f_'),
            'msg':          msg
        }


class ViewProfilePage(UserSettingsPage):
    """
    Redirect to the user profile page.
    """

    settings_page_identifier = 'viewprofile'

    def get_settings_link_title(self, req):
        _ = req.gettext
        return _('View Profile')

    def get_settings_page(self, req):
        return HttpRedirect('users/%s' % urlencode(req.user.username))
