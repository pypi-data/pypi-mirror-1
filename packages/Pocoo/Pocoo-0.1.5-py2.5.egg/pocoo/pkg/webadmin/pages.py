# -*- coding: utf-8 -*-
"""
    pocoo.pkg.webadmin.pages
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.db import meta
from pocoo.http import PageNotFound
from pocoo.pkg.webadmin.base import AdminPage
from pocoo.pkg.webadmin.forms import GeneralSettingsForm, CacheSettingsForm, \
     SecuritySettingsForm, EmailSettingsForm, AvatarSettingsForm, \
     SignatureSettingsForm, BoardSettingsForm, ForumEditForm, EditUserForm, \
     AddUserForm

from pocoo.pkg.core.textfmt import get_markup_formatters
from pocoo.pkg.core.auth import get_auth_provider_mapping
from pocoo.pkg.core.db import forums
from pocoo.pkg.core.user import User


class GeneralSettings(AdminPage):
    category = 'settings'
    identifier = 'general'

    def get_title(self, req):
        _ = req.gettext
        return _('General')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage general settings (serverpath, packages, database etc)')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        auth_modules = [(x, x) for x in get_auth_provider_mapping(self.ctx)]
        auth_modules.sort(key=lambda x: x[0].lower())

        form = GeneralSettingsForm(req, self, 'POST', {
            'serverpath':   cfg.get('general', 'serverpath', ''),
            'packages':     u'\n'.join(cfg.get('general', 'packages', [])),
            'auth_module':  cfg.get('general', 'auth_module', 'SessionAuth'),
            'dburi':        cfg.get('database', 'uri', '')
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                cfg.set('general', 'packages', d.pop('packages').splitlines())
                cfg.set('database', 'uri', d.pop('dburi'))
                for key, value in d.iteritems():
                    cfg.set('general', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/general.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }


class CacheSettings(AdminPage):
    category = 'settings'
    identifier = 'caching'

    def get_title(self, req):
        _ = req.gettext
        return _('Caching')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage the caching system')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = CacheSettingsForm(req, self, 'POST', {
            'enabled':              cfg.get_bool('cache', 'enabled', True),
            'template_memcache':    cfg.get_bool('cache', 'template_memcache', True),
            'template_diskcache':   cfg.get_bool('cache', 'template_diskcache', False),
            'static_cache':         cfg.get_bool('cache', 'static_cache', True)
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                for key, value in d.iteritems():
                    cfg.set('cache', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/cache.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }


class SecuritySettings(AdminPage):
    category = 'settings'
    identifier = 'security'

    def get_title(self, req):
        _ = req.gettext
        return _('Security')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage the security settings (user activation, '
                 'password strength etc)')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = SecuritySettingsForm(req, self, 'POST', {
            'password_strength': cfg.get('security', 'password_strength', '3'),
            'activation_level':  cfg.get('security', 'activation_level', '1'),
            'username_change':   cfg.get_bool('security', 'username_change', False)
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                for key, value in d.iteritems():
                    cfg.set('security', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/security.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }


class EmailSettings(AdminPage):
    category = 'settings'
    identifier = 'email'

    def get_title(self, req):
        _ = req.gettext
        return _('Email')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage the email server settings')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = EmailSettingsForm(req, self, 'POST', {
            'admin_mails':      u'\n'.join(cfg.get('general', 'admin_mails')),
            'send_error_mails': cfg.get_bool('general', 'send_error_mails'),
            'mail_host':        cfg.get('email', 'host', 'localhost'),
            'mail_user':        cfg.get('email', 'user', ''),
            'mail_pass':        cfg.get('email', 'pass', ''),
            'mail_prefix':      cfg.get('email', 'prefix', '[pocoo] '),
            'mail_suffix':      cfg.get('email', 'suffix', ''),
            'mail_signature':   cfg.get('email', 'signature', 'Your pocoo team')
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                cfg.set('general', 'admin_mails',
                        d.pop('admin_mails'))
                cfg.set('general', 'send_error_mails',
                        d.pop('send_error_mails'))
                for key, value in d.iteritems():
                    # cut off "mail_" prefix
                    cfg.set('email', key[5:], value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/email.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }


class AvatarSettings(AdminPage):
    category = 'settings'
    identifier = 'avatars'

    def get_title(self, req):
        _ = req.gettext
        return _('Avatars')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage avatar related settings')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = AvatarSettingsForm(req, self, 'POST', {
            'allow_avatars':    cfg.get_bool('board', 'allow_avatars', True),
            'avatar_dimension': cfg.get_int('board', 'avatar_dimension', 80)
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                for key, value in d.iteritems():
                    cfg.set('board', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/avatar.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }



class SignatureSettings(AdminPage):
    category = 'settings'
    identifier = 'signature'

    def get_title(self, req):
        _ = req.gettext
        return _('Signature')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage signature filters or disable signatures entirely')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = SignatureSettingsForm(req, self, 'POST', {
            'signature_length': cfg.get_int('board', 'signature_length', 255),
            'signature_lines':  cfg.get_int('board', 'signature_lines', 3)
        })
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                for key, value in d.iteritems():
                    cfg.set('board', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/signature.html', {
            'msg':      msg,
            'form':     form.generate(prefix='f_')
        }


class BoardSettings(AdminPage):
    category = 'settings'
    identifier = 'board'

    def get_title(self, req):
        _ = req.gettext
        return _('Board')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage forum settings like the board title, description, '
                 'favicon, forum defaults etc.')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        cfg = req.ctx.cfg

        form = BoardSettingsForm(req, self, 'POST', {
            'title':            cfg.get('board', 'title'),
            'description':      cfg.get('board', 'description'),
            'logo':             cfg.get('board', 'logo'),
            'favicon':          cfg.get('board', 'favicon'),
            'redirecttime':     cfg.get_int('board', 'redirecttime'),
            'autologin':        cfg.get_bool('board', 'autologin'),
            'enable_coppa':     cfg.get_bool('board', 'enable_coppa'),
            'cookieexpire':     cfg.get_int('board', 'cookieexpire'),
            'cookiename':       cfg.get('board', 'cookiename'),
            'default_view':     cfg.get('board', 'default_view'),
            'posts_per_page':   cfg.get_int('board', 'posts_per_page'),
            'threads_per_page': cfg.get_int('board', 'threads_per_page'),
            'syntax_parser':    cfg.get('board', 'syntax_parser')
        })

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                for key, value in d.iteritems():
                    cfg.set('board', key, value)
                cfg.save()
                msg = _('Changes saved')

        return 'webadmin/settings/board.html', {
            'msg':          msg,
            'form':         form.generate(prefix='f_')
        }


class ForumsSettings(AdminPage):
    category = 'forum'
    identifier = 'forums'
    #XXX: this page looks like a big, big hack. any ideas?

    def get_title(self, req):
        _ = req.gettext
        return _('Forums')

    def get_description(self, req):
        _ = req.gettext
        return _('Manage forums and categories')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None
        forum_list = []
        f = forums.c
        engine = self.ctx.engine
        forum_id = req.args.get('forum') or None
        this_forum = None
        this_url = self.url
        if forum_id:
            this_url += '?forum=%s' % forum_id

        if forum_id is not None:
            row = engine.execute(meta.select([f.name, f.parent_id],
                                 f.forum_id == forum_id)).fetchone()
            if row is None:
                return PageNotFound()
            parent_url = self.url
            if row['parent_id'] is not None:
                parent_url += '?forum=%s' % row['parent_id']
            this_forum = {
                'name':         row['name'],
                'forum_id':     forum_id,
                'url':          self.ctx.make_url(self.url + '?forum=%s' %
                                                  forum_id),
                'parent_url':   parent_url
            }

        for forum in engine.execute(meta.select([f.forum_id, f.name,
                                                 f.description,
                                                 f.position, f.link],
                                    f.parent_id == forum_id)):
            form = ForumEditForm(req, this_url, 'POST', dict(forum))

            # check if this form was modified
            if req.method == 'POST' and \
               req.form.get('f_forum_id') == unicode(forum['forum_id']):
                form.update(req.form, prefix='f_')
                if not form.has_errors:
                    engine.execute(forums.update(
                        f.forum_id == forum['forum_id']
                    ), **form.to_dict())
                    msg = _('Saved changes')
                else:
                    msg = _('Could not save changes, see the error '
                            'messages below')

            d = form.generate(prefix='f_')
            d['delete_url'] = self.ctx.make_url(self.url + '?delete=%s' %
                                                forum['forum_id'])
            d['switch_url'] = self.ctx.make_url(self.url + '?forum=%s' %
                                                forum['forum_id'])
            # save to position (either the newly submitted of the
            # original as fallback) in the dict so that we can
            # sort the list later
            try:
                d['form_position'] = int(d['position']['value'])
            except ValueError:
                d['form_position'] = forum['position']
            forum_list.append(d)

        # order by position (might be updated)
        forum_list.sort(key=lambda x: x['form_position'])

        add_form = ForumEditForm(req, self, 'POST', {'forum_id': 0})

        return 'webadmin/settings/forums.html', {
            'msg':          msg,
            'forums':       forum_list,
            'forum':        this_forum,
            'add_form':     add_form.generate(prefix='f_')
        }



class EditUser(AdminPage):
    category = 'user'
    identifier = 'edituser'

    def get_title(self, req):
        _ = req.gettext
        return _('Edit User')

    def get_description(self, req):
        _ = req.gettext
        return _("Alter a user's settings")

    def get_admin_page(self, req):
        _ = req.gettext
        user = new_username = msg = None

        if req.method == 'POST':
            if req.form.get('f_user_id'):
                user = User(req.ctx, int(req.form['f_user_id']))
            else:
                try:
                    user = User.by_name(req.ctx, req.form['f_search_username'])
                except User.NotFound:
                    form = EditUserForm(req, self, 'POST', {})
                    form.update(req.form, prefix='f_')
                    return 'webadmin/settings/edituser.html', {
                        'user':     None,
                        'form':     form.generate(prefix='f_')
                    }

            get_setting = lambda x: user.profile.get(x, u'')

            form = EditUserForm(req, self, 'POST', {
                'user_id':      user.user_id,
                'username':     user.username,
                'email':        user.email,
                'new_password':     '',
                'show_email':   user.settings.get('show_email') or False,
                'aol':    get_setting('aol'),
                'icq':    get_setting('icq'),
                'jabber':    get_setting('jabber'),
                'msn':    get_setting('msn'),
                'yahoo':    get_setting('yahoo'),
                'website':    get_setting('website'),
                'interests':    get_setting('interests')
            })

            form.update(req.form, prefix='f_')

            if not form.has_errors and req.form.get('f_user_id'):
                msg = _('Saved changes')
                d = form.to_dict()
                d.pop('user_id')
                new_username = d.pop('username')
                if new_username != d.pop('search_username'):
                    user.username = new_username
                user.email = d.pop('email')
                new_password = d.pop('new_password')
                if new_password:
                    user.set_password(new_password)
                user.settings.update({'show_email': d.pop('show_email')})
                user.profile.update(d)
                user.save()
        else:
            form = EditUserForm(req, self, 'POST', {})

        f = form.generate(prefix='f_')

        f['search_username']['value'] = new_username or f['search_username']['value']

        return 'webadmin/settings/edituser.html', {
            'user':     user and {'user_id': user.user_id} or False,
            'form':     f,
            'msg':      msg
        }


class AddUser(AdminPage):
    category = 'user'
    identifier = 'adduser'

    def get_title(self, req):
        _ = req.gettext
        return _('New User')

    def get_description(self, req):
        _ = req.gettext
        return _('Create a new user')

    def get_admin_page(self, req):
        _ = req.gettext
        msg = None

        form = AddUserForm(req, self, 'POST', {})

        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                d = form.to_dict()
                user = User.create(req.ctx, d.pop('username'), d.pop('new_password'),
                    d.pop('email'), False)
                user.settings.update({'show_email': d.pop('show_email')})
                user.profile.update(d)
                user.save()
                form = AddUserForm(req, self, 'POST', {})
                msg = _('The user was successfully created.')

        return 'webadmin/settings/adduser.html', {
            'form': form.generate(prefix='f_'),
            'msg':  msg
        }
