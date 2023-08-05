# -*- coding: utf-8 -*-
"""
    pocoo.utils.text
    ~~~~~~~~~~~~~~~~

    Miscellaneous text processing functions.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from random import choice, randrange
import sha
import md5
import os
import string  # pylint: disable-msg=W0402

KEY_CHARS = string.ascii_letters + string.digits
SALT_CHARS = string.ascii_lowercase + string.digits


def to_utf8(text, charset='iso-8859-15'):
    """
    Convert a string to UTF-8, assuming the encoding is either UTF-8, ISO
    Latin-1, or as specified by the optional ``charset`` parameter.
    """
    # originally taken from trac:
    # http://projects.edgewall.com/trac/browser/trunk/trac/util.py
    try:
        # if already unicode return it
        u = unicode(text, 'utf-8')
        return text
    except TypeError:
        if isinstance(text, unicode):
            return text.encode('utf-8')
        raise
    except UnicodeError:
        try:
            # user defined charset
            u = unicode(text, charset)
        except UnicodeError:
            # fallback to iso-8859-15
            u = unicode(text, 'iso-8859-15')
        return u.encode('utf-8')


def gen_salt(length=6):
    """
    Generate a random string of SALT_CHARS with specified ``length``.
    """
    return ''.join(choice(SALT_CHARS) for _ in xrange(length))


def gen_activation_key(length=8):
    """
    Generate a ``length`` long string of KEY_CHARS, suitable as
    password or activation key.
    """
    return ''.join(choice(KEY_CHARS) for _ in xrange(length))


def gen_password(length=8, add_numbers=True, mix_case=True,
                 add_special_char=True):
    """
    Generate a pronounceable password.
    """
    consonants = 'bcdfghjklmnprstvwz'
    vowels = 'aeiou'
    if mix_case:
        consonants = consonants*2 + consonants.upper()
        vowels = vowels*2 + vowels.upper()
    pw =  ''.join([choice(consonants) +
                   choice(vowels) +
                   choice(consonants + vowels) for _
                   in xrange(length // 3 + 1)])[:length]
    if add_numbers:
        n = length // 3
        if n > 0:
            pw = pw[:-n]
            for _ in xrange(n):
                pw += choice('0123456789')
    if add_special_char:
        tmp = randrange(0, len(pw))
        l1 = pw[:tmp]
        l2 = pw[tmp:]
        if max(len(l1), len(l2)) == len(l1):
            l1 = l1[:-1]
        else:
            l2 = l2[:-1]
        return l1 + choice('#$&%?!') + l2
    return pw


def gen_pwhash(password):
    """
    Return a the password encrypted in sha format with a random salt.
    """
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = gen_salt(6)
    h = sha.new()
    h.update(salt)
    h.update(password)
    return 'sha$%s$%s' % (salt, h.hexdigest())


def gen_hash():
    """
    Generate a random 32-bit hash.
    """
    return md5.new(os.urandom(40)).hexdigest()


def random_form_uid():
    """
    Generate a random form uid for XSS (cross-site scripting) prevention.
    """
    return os.urandom(40).encode('base64')[:-3]


def split_format(format):
    """
    Split a strftime format into an iterable of strings and format
    items (``%x`` units).
    """
    p = c = f = 0
    l = len(format)
    while c < l:
        if f:
            yield '%' + format[c]
            f = 0
            p = c+1
        elif format[c] == '%':
            if p < c:
                yield format[p:c]
            f = 1
        c += 1
    if p < l:
        yield format[p:]


def check_pwhash(pwhash, password):
    """
    Check a password against a given hash value. Since
    many forums save md5 passwords with no salt and it's
    technically impossible to convert this to an sha hash
    with a salt we use this to be able to check for
    plain passwords::

        plain$$default

    md5 passwords without salt::

        md5$$c21f969b5f03d33d43e04f8f136e7682

    md5 passwords with salt::

        md5$123456$7faa731e3365037d264ae6c2e3c7697e

    sha passwords::

        sha$123456$118083bd04c79ab51944a9ef863efcd9c048dd9a

    Note that the integral passwd column in the table is
    only 60 chars long. If you have a very large salt
    or the plaintext password is too long it will be
    truncated.
    """
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    if pwhash.count('$') < 2:
        return False
    method, salt, hashval = pwhash.split('$', 2)
    if method == 'plain':
        return hashval == password
    elif method == 'md5':
        h = md5.new()
    elif method == 'sha':
        h = sha.new()
    else:
        return False
    h.update(salt)
    h.update(password)
    return h.hexdigest() == hashval
