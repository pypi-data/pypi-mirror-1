# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.validators
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Special validation, in addition to `pocoo.utils.validators`.

    For a general explanation of the validators system, please
    see `pocoo.utils.form`.


    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
import unicodedata
from pocoo.utils.validators import ValidationError, _mail_re
from pocoo.pkg.core.user import User, get_id_by_name

_icq_re = re.compile(r'^\d{6,9}$')


# pylint: disable-msg=C0103

def isValidUsername():
    """Checks if the given string looks like a valid username."""
    def is_valid_username(field, form):
        errors = []
        _ = lambda s: errors.append(form.req.gettext(s))
        value = field.value.strip()
        if len(value) < 2:
            _('Please enter a username that is at least 2 characters long.')
        if len(value) > 30:
            _('Please enter a username that is no longer than 30 characters.')
        for char in value:
            if char in '_-. ':
                continue
            if unicodedata.category(char)[0] not in 'LN':
                _('Please enter a username without special characters '
                  'except "_", "-", ".".')
                break
        if errors:
            raise ValidationError(*errors)
    return is_valid_username


def isAvailableUsername():
    """Checks if the username is valid and available."""
    def is_available_username(field, form):
        isValidUsername()(field, form)
        try:
            get_id_by_name(form.req.ctx, field.value)
        except User.NotFound:
            return
        _ = form.req.gettext
        raise ValidationError(_('The username is already in use.'))
    return is_available_username


def isAnonymousUsername():
    """Checks if this is a valid username for anonymous usage."""
    def is_anonymous_username(field, form):
        if field.value != 'anonymous':
            isAvailableUsername()(field, form)
    return is_anonymous_username


def isExistingUsername():
    """Checks if the username does exist."""
    def is_existing_username(field, form):
        try:
            get_id_by_name(form.req.ctx, field.value)
            return
        except User.NotFound:
            _ = form.req.gettext
            raise ValidationError(_('The user %s does not exist.') % field.value)
    return is_existing_username


def isStrongPassword(strength=None):
    """Checks if the password is strong enough"""
    def is_strong_password(field, form):
        errors = []
        _ = lambda s: errors.append(form.req.gettext(s))
        if strength is None:
            s = form.req.ctx.cfg.get_int('security', 'password_strength', 3)
        else:
            s = strength
        s = max(0, min(4, s))
        if not s and not field.value:
            _('Please fill out the password field.')
        elif s == 1:
            if len(field.value) < 4:
                _('Please enter a password with at least 4 characters.')
        elif s == 2:
            if len(field.value) < 6:
                _('Please enter a password with at least 6 characters.')
        elif s == 3:
            def test():
                have_letter = have_number = False
                for char in field.value:
                    c = unicodedata.category(char)[0]
                    if c == 'L':
                        have_letter = True
                    elif c == 'N':
                        have_number = True
                    if have_letter and have_number:
                        return True
                return False
            if len(field.value) < 6 or not test():
                _('Please enter a password with at least 6 characters which '
                  'contains both letters and numbers.')
        elif s == 4:
            def test():
                have_letter = have_number, have_special = False
                for char in field.value:
                    c = unicodedata.category(char)[0]
                    if c == 'L':
                        have_letter = True
                    elif c == 'N':
                        have_number = True
                    elif c == 'S':
                        have_special = True
                    if have_letter and have_number and have_special:
                        return True
                return False
            if len(field.value) < 6 or not test():
                _('Please enter a password with at least 6 characters with '
                  'contains of letters, numbers and at least one special '
                  'character.')
        if errors:
            raise ValidationError(*errors)
    return is_strong_password



def isValidSignature():
    """Checks if the signature is valid."""
    def is_valid_signature(field, form):
        errors = []
        _ = lambda s: errors.append(form.req.gettext(s))
        val = field.value.strip()
        max_len = form.req.ctx.cfg.get_int('board', 'signature_length')
        max_lines = form.req.ctx.cfg.get_int('board', 'signature_lines')
        if len(val) > max_len:
            _('Your signature must not be longer than %d characters.') % max_len
        if len(val.splitlines()) > max_lines:
            _('Your signature must not be longer than %d lines.') % max_lines
        if errors:
            raise ValidationError(*errors)
    return is_valid_signature


def isIcqMessengerId():
    """Checks if the value is a valid ICQ ID"""
    def is_icq_messenger_id(field, form):
        if _icq_re.search(field.value) is None:
            _ = form.req.gettext
            raise ValidationError(_('Please enter a valid ICQ ID'))
    return is_icq_messenger_id


def isJabberMessengerId():
    """Checks if the value is a valid jabber ID"""
    def is_jabber_messenger_id(field, form):
        if _mail_re.search(field.value) is None:
            _ = form.req.gettext
            raise ValidationError(_('Please enter a valid jabber ID'))
    return is_jabber_messenger_id


def isMsnMessengerId():
    """Checks if the value is a valid MSN ID"""
    def is_msn_messenger_id(field, form):
        if _mail_re.search(field.value) is None:
            _ = form.req.gettext
            raise ValidationError(_('Please enter a valid MSN ID.'))
    return is_msn_messenger_id


# TODO: I don't know how valid AIM and Y!M IDs look, so I can't write validators
#       for them. It looks like they are simple strings, but I'm not sure...
