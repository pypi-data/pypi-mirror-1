# -*- coding: utf-8 -*-
"""
    pocoo.utils.uri
    ~~~~~~~~~~~~~~~

    URI processing utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import urllib


def urlencode(*args, **kwargs):
    """
    Like urllib.urlencode but takes also unicode objects
    which are automatically encoded in utf-8.
    The returned object is an ascii encoded unicode object.

    If the first argument is a string or unicode, it
    will be used to urlencode the first part of the url,
    right before the question mark.
    """
    if args and isinstance(args[0], basestring):
        root, args = args[0], args[1:]
        url = unicode(urllib.quote(root.encode('utf-8')))
    else:
        url = u''
    tmp = {}
    for key, value in dict(*args, **kwargs).iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        elif isinstance(value, unicode):
            value = value.encode('utf-8')
        tmp[key] = value
    return (tmp and url + '?' or url) + urllib.urlencode(tmp)
