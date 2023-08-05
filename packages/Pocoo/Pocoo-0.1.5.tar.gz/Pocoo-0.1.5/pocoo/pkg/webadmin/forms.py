# -*- coding: utf-8 -*-
"""
    pocoo.pkg.webadmin.forms
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.utils import forms
from pocoo.utils.validators import isNotEmpty, mayEmpty, isInteger, \
    checkTextLength, doLineCheck, isEmail, isValidUrl, ValidationError, isSameValue, \
    checkIfOtherNotBlank
from pocoo.pkg.core.validators import isAvailableUsername, isExistingUsername, \
     isIcqMessengerId, isMsnMessengerId, isJabberMessengerId, isYahooMessengerId
from pocoo.pkg.core.textfmt import get_markup_formatters
from pocoo.pkg.core.auth import get_auth_provider_mapping


class GeneralSettingsForm(forms.Form):
    """Form for `pocoo.pkg.webadmin.pages.GeneralSettings`"""

    def get_auth_module(field, form):
        auth_modules = [(x, x) for x in get_auth_provider_mapping(form.ctx)]
        auth_modules.sort(key=lambda x: x[0].lower())
        return auth_modules

    serverpath = forms.TextField(isValidUrl())
    packages = forms.TextArea()
    auth_module = forms.SelectBox(get_auth_module)
    dburi = forms.TextField(isValidUrl(schemes=['sqlite', 'postgres', 'mysql',
                                              'mssql', 'oracle', 'firebird']))


class CacheSettingsForm(forms.Form):
    """Form for `pocoo.pkg.webadmin.pages.CacheSettigs`"""
    enabled = forms.CheckBox()
    template_memcache = forms.CheckBox()
    template_diskcache = forms.CheckBox()
    static_cache = forms.CheckBox()


class SecuritySettingsForm(forms.Form):
    """Form for `pocoo.pkg.webadmin.pages.SecuritySettings`"""
    def get_password_strength_choices(field, form):
        _ = form.req.gettext
        return [
            ('0',   _('not empty')),
            ('1',   _('at least 4 chars')),
            ('2',   _('at least 6 chars')),
            ('3',   _('at least 6 chars, including letters and '
                      'numbers')),
            ('4',   _('at least 6 chars, including letters, numbers '
                      'and special characters'))
        ]

    def get_activation_level_choices(field, form):
        _ = form.req.gettext
        return [
            ('0',   _('automatic activation')),
            ('1',   _('email activation')),
            ('2',   _('manual activation by administrator'))
        ]

    password_strength = forms.SelectBox(get_password_strength_choices)
    activation_level = forms.SelectBox(get_activation_level_choices)
    username_change = forms.CheckBox()


class EmailSettingsForm(forms.Form):
    """Form used by `pocoo.pkg.webadmin.pages.EmailSettings`"""
    admin_mails = forms.TextArea(doLineCheck(isEmail(allow_verbose=True)))
    send_error_mails = forms.CheckBox()
    mail_host = forms.TextField()
    mail_user = forms.TextField()
    mail_pass = forms.TextField()
    mail_from = forms.TextField(isEmail(allow_verbose=True))
    mail_prefix = forms.TextField()
    mail_suffix = forms.TextField()
    mail_signature = forms.TextField()


class AvatarSettingsForm(forms.Form):
    """Form used by `pocoo.pkg.webadmin.pages.AvatarSettings`"""
    allow_avatars = forms.CheckBox()
    avatar_dimension = forms.TextField(isInteger())


class SignatureSettingsForm(forms.Form):
    """Form used by `pocoo.pkg.webadmin.pages.SignatureSettings`"""
    signature_length = forms.CheckBox(isInteger())
    signature_lines = forms.TextField(isInteger())


class BoardSettingsForm(forms.Form):
    """Form used by `pocoo.pkg.webadmin.pages.BoardSettings`"""

    def get_default_view_choices(field, form):
        _ = form.req.gettext
        return [
            ('threaded', _('Threaded')),
            ('flat', _('Flat'))
        ]

    def get_markup_parser_choices(field, form):
        return get_markup_formatters(form.req)

    title = forms.TextField(isNotEmpty())
    description = forms.TextArea(mayEmpty())
    logo = forms.TextField(mayEmpty())
    favicon = forms.TextField(mayEmpty())
    redirecttime = forms.TextField(isInteger(), int)
    autologin = forms.CheckBox()
    enable_coppa = forms.CheckBox()
    cookieexpire = forms.TextField(isInteger, int)
    cookiename = forms.TextField(checkTextLength(5, 20))
    default_view = forms.SelectBox(get_default_view_choices)
    posts_per_page = forms.TextField(isInteger(), int)
    threads_per_page = forms.TextField(isInteger(), int)
    syntax_parser = forms.SelectBox(get_markup_parser_choices)


class ForumEditForm(forms.Form):
    forum_id = forms.HiddenField(int)
    name = forms.TextField(isNotEmpty())
    description = forms.TextArea()
    position = forms.TextField(isInteger())
    link = forms.TextField(mayEmpty(isValidUrl()))


class EditUserForm(forms.Form):
    def is_available_or_own_username():
        def func(field, form):
            try:
                isSameValue('search_username', lambda x,y: x)(field, form)
            except ValidationError:
                isAvailableUsername()(field, form)
        return func

    search_username = forms.TextField(isExistingUsername())
    user_id = forms.HiddenField()
    username = forms.TextField(checkIfOtherNotBlank('user_id', \
        is_available_or_own_username()))
    new_password = forms.PasswordField(isNotEmpty())

    email = forms.TextField(checkIfOtherNotBlank('user_id', isEmail()))
    show_email = forms.CheckBox()
    aol = forms.TextField(mayEmpty())
    icq = forms.TextField(mayEmpty(isIcqMessengerId()))
    jabber = forms.TextField(mayEmpty(isJabberMessengerId()))
    msn = forms.TextField(mayEmpty(isMsnMessengerId()))
    yahoo = forms.TextField(mayEmpty(isYahooMessengerId()))
    website = forms.TextField(mayEmpty(isValidUrl()))
    location = forms.TextField(checkTextLength(0, 255))
    interests = forms.TextArea(checkTextLength(0, 512))


class AddUserForm(forms.Form):
    username = forms.TextField(isAvailableUsername())
    new_password = forms.PasswordField(isNotEmpty())
    email = forms.TextField(isEmail())
    show_email = forms.CheckBox()
    aol = forms.TextField(mayEmpty())
    icq = forms.TextField(mayEmpty(isIcqMessengerId()))
    jabber = forms.TextField(mayEmpty(isJabberMessengerId()))
    msn = forms.TextField(mayEmpty(isMsnMessengerId()))
    yahoo = forms.TextField(mayEmpty(isYahooMessengerId()))
    website = forms.TextField(mayEmpty(isValidUrl()))
    location = forms.TextField(checkTextLength(0, 255))
    interests = forms.TextArea(checkTextLength(0, 512))
