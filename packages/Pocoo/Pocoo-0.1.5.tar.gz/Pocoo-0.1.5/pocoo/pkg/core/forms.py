# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.forms
    ~~~~~~~~~~~~~~~~~~~~

    Pocoo Forms.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.utils import forms
from pocoo.utils.validators import isNotEmpty, isEmail, isSameValue, \
     checkTextLength, mayEmpty, isOneLetter, isExistingUrl, \
     isSupportedImage, doMultiCheck, isInteger, isInRange
from pocoo.pkg.core.validators import isAvailableUsername, \
     isStrongPassword, coppaIsChecked, isExistingUsername, \
     isAnonymousUsername, isValidSignature, isAimMessengerId, \
     isIcqMessengerId, isMsnMessengerId, isJabberMessengerId, \
     isYahooMessengerId


def get_password_error(form, field):
    _ = form.req.gettext
    return _('The two passwords don\'t match.')


def int_or_none(val):
    """manipulator which returns an int or None"""
    try:
        return int(val)
    except ValueError:
        return None


class LoginForm(forms.Form):
    """Form used by `pkg.core.pages.LoginPage`"""
    username = forms.TextField(isNotEmpty())
    password = forms.PasswordField(isNotEmpty())


class RegisterForm(forms.Form):
    """Form used by `pkg.core.pages.RegisterPage`"""
    username = forms.TextField(isAvailableUsername())
    email = forms.TextField(isEmail())
    password = forms.PasswordField(isStrongPassword())
    password2 = forms.PasswordField(isSameValue('password',
                                                get_password_error))
    coppa = forms.CheckBox(coppaIsChecked())


class LostPasswordForm(forms.Form):
    """Form used by `pkg.core.pages.LostPasswordPage`"""
    username = forms.TextField(isExistingUsername())
    email = forms.TextField(isEmail())


class NewPostForm(forms.Form):
    """Form used by `pkg.core.pages.NewPostPage` and
    `pkg.core.pages.NewThreadPage`"""
    username = forms.TextField(isAnonymousUsername())
    title = forms.TextField(isNotEmpty())
    text = forms.TextArea(checkTextLength(3, 15000))


class MemberListForm(forms.Form):
    """Form used by `pkg.core.pages.MemberListPage`"""

    def get_order_by(field, form):
        _ = form.req.gettext
        return [
            ('user_id',         _('User ID')),
            ('username',        _('Username')),
            ('register_date',   _('Register date')),
            ('post_count',      _('Number of Posts'))
        ]

    def get_direction(field, form):
        _ = form.req.gettext
        return [
            ('desc',            _('Descending')),
            ('asc',             _('Ascending'))
        ]

    letter = forms.TextField(mayEmpty(isOneLetter()))
    order_by = forms.SelectBox(get_order_by)
    direction = forms.SelectBox(get_direction)


class UserSignatureForm(forms.Form):
    """Form used by `pkg.core.usersettings.UserSignatureSettings`"""
    signature = forms.TextArea(isValidSignature())


class UserProfileForm(forms.Form):
    """Form used by `pkg.core.usersettings.UserProfileSettings`"""
    new_password = forms.PasswordField(mayEmpty(isStrongPassword()))
    new_password2 = forms.PasswordField(isSameValue('new_password',
                                                    get_password_error))
    email = forms.TextField(isEmail())
    show_email = forms.CheckBox()
    aol = forms.TextField(mayEmpty(isAimMessengerId()))
    icq = forms.TextField(mayEmpty(isIcqMessengerId()))
    jabber = forms.TextField(mayEmpty(isJabberMessengerId()))
    msn = forms.TextField(mayEmpty(isMsnMessengerId()))
    yahoo = forms.TextField(mayEmpty(isYahooMessengerId()))
    website = forms.TextField(mayEmpty(isExistingUrl()))
    location = forms.TextField(checkTextLength(0, 255))
    interests = forms.TextArea(checkTextLength(0, 512))


class AvatarForm(forms.Form):
    """Form used by `pkg.core.usersettings.AvatarSettings`"""
    avatar = forms.FileField(mayEmpty(isSupportedImage()))
    delete_avatar = forms.CheckBox()


class UserForumSettingsForm(forms.Form):
    """Form used by `pkg.core.usersettings.UserForumSettings`"""

    def get_view_mode(field, form):
        _ = form.req.gettext
        return [
            ('',            _('default')),
            ('threaded',    _('threaded')),
            ('flat',        _('flat'))
        ]

    posts_per_page = forms.TextField(mayEmpty(doMultiCheck(
                                     isInteger(), isInRange(5, 50))),
                                     int_or_none)
    threads_per_page = forms.TextField(mayEmpty(doMultiCheck(
                                       isInteger(), isInRange(10, 80))),
                                       int_or_none)
    view_mode = forms.SelectBox(get_view_mode)
    ajax = forms.CheckBox()
