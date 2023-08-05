# -*- coding: utf-8 -*-
"""
    pocoo.utils.net
    ~~~~~~~~~~~~~~~

    Network utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import socket
import urlparse


def make_url_context_external(ctx, url):
    """
    Check if an URL is on the same server as the context.
    """
    check = urlparse.urljoin(ctx.serverpath, url)
    u1 = urlparse.urlsplit(ctx.serverpath)[:2]
    u2 = urlparse.urlsplit(check)[:2]
    if u1 != u2:
        raise ValueError('the url is not on the same server')
    return check


def is_ipv4_addr(addr):
    """
    Return True if the given address is a valid IPv4 address.
    """
    parts = addr.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            part = int(part)
        except ValueError:
            return False
        if part > 255 or part < 0:
            return False
    return True


def is_ipv6_addr(addr):
    """
    Return True if the given address is a valid IPv6 address.
    """
    hexchars = set('0123456789abcdefABCDEF')
    parts = addr.split(':')
    if len(parts) > 8 or len(parts) < 2:
        return False
    for part in parts:
        pset = set(part)
        if not pset.issubset(hexchars) or len(part) > 4:
            return False
    return True


def ipv4_to_ipv6(addr):
    """
    Convert an IPv4 address to IPv6.
    """
    if not is_ipv4_addr(addr):
        raise ValueError, 'IPv4 address required'
    parts = [hex(int(p))[2:] for p in addr.split('.')]
    result = '2002:'
    for pos, part in enumerate(parts):
        if len(part) == 1:
            part = '0' + part
        result += part
        if pos % 2 != 0:
            result += ':'
    return result + ':'


def ipv6_to_ipv4(addr):
    """
    Convert an IPv6 6to4 address back to IPv4.
    """
    if not is_ipv6_addr(addr):
        raise ValueError, 'IPv6 address required'
    if not addr.startswith('2002:'):
        raise ValueError, '%s is not a valid 6to4 address.' % addr
    parts = ''.join(addr.split(':')[1:-2])
    parts = [parts[i:i+2] for i in xrange(0, len(parts), 2)]
    return '%d.%d.%d.%d' % tuple(int(p, 16) for p in parts)


# pylint: disable-msg=W0201,R0904

class IP(str):
    """
    Represents one IPv4 address.
    """

    def __init__(self, addr):
        str.__init__(self, addr)
        if is_ipv4_addr(addr):
            self._addr = addr
        else:
            raise TypeError, 'invalid address format'

    def __cmp__(self, other):
        if isinstance(other, IP):
            return cmp(self._addr, other._addr)
        elif isinstance(other, basestring):
            if is_ipv4_addr(other):
                return cmp(self._addr, other)
        raise TypeError, 'invalid comparison'

    def __repr__(self):
        return '<IP %s>' % self

    def __str__(self):
        return self._addr

    def __unicode__(self):
        return unicode(self._addr)

    @staticmethod
    def by_hostname(hostname):
        return IP(socket.gethostbyname(hostname))

    def _fetch_hostname(self):
        if not hasattr(self, '_hostname'):
            try:
                self._hostname = socket.gethostbyaddr(self._addr)
            except socket.herror:
                self._hostname = ('', [''])

    def _get_hostname(self):
        self._fetch_hostname()
        return self._hostname[0]

    def _get_aliases(self):
        self._fetch_hostname()
        return self._hostname[1]

    ip = property(__str__)
    hostname = property(_get_hostname)
    aliases = property(_get_aliases)
