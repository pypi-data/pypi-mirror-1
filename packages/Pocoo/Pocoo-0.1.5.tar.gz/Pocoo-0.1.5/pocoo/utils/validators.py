# -*- coding: utf-8 -*-
"""
    pocoo.utils.validators
    ~~~~~~~~~~~~~~~~~~~~~~

    Builtin validators.

    For documentation about form validation, see `pocoo.utils.form`.


    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
# pylint: disable-msg=C0103
import re
import urllib2
import urlparse
from copy import copy
from pocoo.utils import image

_mail_re = re.compile(
    r'^([a-zA-Z0-9_\.\-])+'
    r'\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,})+$'
)
_mail_title_re = re.compile(r'^.*?<(.*?)>\s*$')

STANDARD_SCHEMES = ('ftp', 'gopher', 'hdl', 'http', 'https', 'imap',
    'mailto', 'mms', 'news', 'nntp', 'prospero', 'rsync', 'rtsp',
    'rtspu', 'shttp', 'sip', 'snews', 'svn', 'svn+ssh', 'telnet', 'wais'
)

class ValidationError(Exception):
    """
    Raised when validation fails.
    """

    def __str__(self):
        return str(self.args)

    def __repr__(self):
        return '<%s: %r>' % (
            self.__class__.__name__,
            self.args
        )


def isNotEmpty():
    """Checks if a field is not empty."""
    def is_not_empty(field, form):
        if not field.value.strip():
            _ = form.req.gettext
            raise ValidationError(_('Please fill out this field.'))
    return is_not_empty


def isLowerCase():
    """Checks if a field contains just lowercase letters."""
    def is_lowercase(field, form):
        if not field.value.islower():
            _ = form.req.gettext
            raise ValidationError(_('this field must be lowercase'))
    return is_lowercase


def isUpperCase():
    """Checks if a field contains just uppercase letters."""
    def is_upper_case(field, form):
        if not field.value.isupper():
            _ = form.req.gettext
            raise ValidationError(_('this field must be uppercase'))
    return is_upper_case


def isInChoiceList(choices):
    """Checks if a SelectBox really contains out of allowed values."""
    def is_in_choice_list(field, form):
        if field.value not in choices:
            _ = form.req.gettext
            raise ValidationError(_('"%s" isn\'t an allowed value') % field.value)
    return is_in_choice_list


def isNotMultiline():
    """Checks if there arn't any newline chars in the field value."""
    def is_not_multiline(field, form):
        if '\n' in field.value or '\r' in field.value:
            _ = form.req.gettext
            raise ValidationError(_('The value must not be multiline'))
    return is_not_multiline


def isSameValue(fieldname, error_callback):
    """
    Checks if a value of this field matches another one.

    If a validation error occours the validator will call the
    `error_callback` with the form as first argument and the
    field as second. This gives you access to the request
    object.
    """
    def is_same_value(field, form):
        if field.value != form.field_map[fieldname].value:
            raise ValidationError(error_callback(form, field))
    return is_same_value


def checkTextLength(minlength=None, maxlength=None):
    """Checks the text length"""
    def check_text_length(field, form):
        errors = []
        _ = form.req.gettext
        curlen = len(field.value)
        if minlength is not None:
            if curlen < minlength:
                errors.append(_('Please enter a value that is at least %d '
                                'characters long. You entered %d.') %
                              (minlength, curlen))
        if maxlength is not None:
            if curlen > maxlength:
                errors.append(_('Please enter a value that is no longer than '
                                '%d characters. You entered %d.') %
                              (maxlength, curlen))
        if errors:
            raise ValidationError(*errors)
    return check_text_length


def isOneLetter():
    """Checks if the value is one letter long"""
    def is_one_letter(field, form):
        if len(field.value) != 1:
            _ = form.req.gettext
            raise ValidationError(_('Please enter exactly one letter.'))
    return is_one_letter


def isInteger(positive=True, negative=True):
    """Performs an integer check"""
    if not (positive or negative):
        raise TypeError('neither positive nor negative allowed')
    def is_integer(field, form):
        errors = []
        _ = form.req.gettext
        try:
            value = int(field.value)
            if int(field.value) != float(field.value):
                raise ValueError()
        except ValueError:
            errors.append(_('Please enter a integer.'))
        else:
            if not negative and value < 0:
                errors.append(_('Please enter a positive integer.'))
            if not positive and value >= 0:
                errors.append(_('Please enter a negative integer.'))
        if errors:
            raise ValidationError(*errors)
    return is_integer


def isNumber(positive=True, negative=True):
    """Performs an integer/float check"""
    if not (positive or negative):
        raise TypeError('neither positive nor negative allowed')
    def is_number(field, form):
        errors = []
        _ = form.req.gettext
        try:
            value = float(field.value)
        except ValueError:
            errors.append(_('Please enter a number.'))
        else:
            if not negative and value < 0:
                errors.append(_('Please enter a positive number.'))
            if not positive and value >= 0:
                errors.append(_('Please enter a negative number.'))
        if errors:
            raise ValidationError(*errors)
    return is_number


def isEmail(allow_verbose=False):
    """
    Checks if the value is a valid mail address.

    If `allow_verbose` is true an optional sender name is allowed.
    eg: ``Foo Bar <foo@bar.com>``.
    """
    def is_email(field, form):
        test = field.value
        if allow_verbose:
            m = _mail_title_re.search(test)
            if m is not None:
                test = m.group(1)
        if _mail_re.search(test) is None:
            _ = form.req.gettext
            raise ValidationError(_('Please enter a valid e-mail address.'))
    return is_email


def matchesRegex(regex, error):
    """Checks if a value matches a regex."""
    def matches_regex(field, form):
        if re.search(regex, field.value) is None:
            raise ValidationError(error)
    return matches_regex


def isValidUrl(schemes=STANDARD_SCHEMES):
    """Checks if a url looks valid. optional it also checks
    if the file really exists."""
    def is_valid_url(field, form):
        try:
            scheme = urlparse.urlparse(field.value)[0]
        except ValueError:
            scheme = None
        if scheme not in schemes:
            _ = form.req.gettext
            raise ValidationError(_('Please enter a valid url.'))
    return is_valid_url


def isExistingUrl():
    """Checks if the given url is an existing http, ftp or gopher url."""
    def is_existing_url(field, form):
        _ = form.req.gettext
        try:
            urllib2.urlopen(field.value)
        except ValueError:
            raise ValidationError(_('Invalid URL: %s') % field.value)
        except:
            raise ValidationError(_('The URL %s is a broken link') %
                                    field.value)
    return is_existing_url


def isSupportedImage():
    """Checks if the thumbnailer can handle this image."""
    def is_supported_image(field, form):
        if not image.is_supported_image(field.value):
            _ = form.req.gettext
            raise ValidationError(_('The uploaded file isn\'t a supported '
                                    'image file.'))
    return is_supported_image


def checkIfOtherNotBlank(fieldname, validator):
    """Performs the wrapped validator only if the given field
    is not empty."""
    def check_if_other_not_blank(field, form):
        if form.field_map[fieldname].value:
            try:
                validator(field, form)
            except ValidationError, err:
                raise err
    return check_if_other_not_blank


def mayEmpty(validator=None):
    """Check the validator just if the field isn't empty."""
    def may_empty(field, form):
        if field.value and validator is not None:
            try:
                validator(field, form)
            except ValidationError, err:
                raise err
    return may_empty


def doMultiCheck(*validators):
    """Checks multiple validators"""
    def do_multi_check(field, form):
        errors = []
        for test in validators:
            try:
                test(field, form)
            except ValidationError, e:
                errors.extend(e.args)
        if errors:
            raise ValidationError(*errors)
    return do_multi_check


def doLineCheck(*validators):
    """Checks each line in the value with all validators."""
    def do_line_check(field, form):
        fields = []
        errors = []
        for line in field.value.splitlines():
            new_field = copy(field)
            new_field.set_value(form, line)
            fields.append(new_field)
        for test in validators:
            for field in fields:
                try:
                    test(field, form)
                except ValidationError, e:
                    errors.extend(e.args)
            if errors:
                raise ValidationError(*errors)
    return do_line_check


def isInRange(minval=None, maxval=None):
    """Checks if a number is in a given range"""
    def is_in_range(field, form):
        errors = []
        _ = form.req.gettext
        # check if the entered value is a number. this doesn't return any
        # error message to avoid messages like "Please enter a integer\n
        # Please enter anumber" when there are other validators
        try:
            num = float(field.value)
        except ValueError:
            raise ValidationError()

        if minval is not None:
            if num < minval:
                errors.append(_('Please enter a value that is bigger than %d')
                                % (minval - 1))
        if maxval is not None:
            if num > maxval:
                errors.append(_('Please enter a value that is smaller than %d')
                                % (maxval + 1))
        if errors:
            raise ValidationError(*errors)
    return is_in_range
