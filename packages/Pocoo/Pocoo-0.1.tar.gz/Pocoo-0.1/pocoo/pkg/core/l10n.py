# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.l10n
    ~~~~~~~~~~~~~~~~~~~

    Pocoo localisation module.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.utils.text import split_format
from datetime import datetime
import time
from calendar import monthrange

# Dateformat Constants
DEFAULT_DATE_FORMAT = '%a, %d %b %Y'
DEFAULT_TIME_FORMAT = '%H:%M'
DEFAULT_DATETIME_FORMAT = '%a, %d %b %Y %H:%M'

# Timedelta Constants
TIME_DELTA_UNITS = [
    (3600 * 24 * 365,   'y'),
    (3600 * 24 * 30,    'M'),
    (3600 * 24 * 7,     'w'),
    (3600 * 24,         'd'),
    (3600,              'h'),
    (60,                'm')
]

# Gettext Helper
_ = lambda x: x

class DateFormatter(object):
    """
    TODO: write documentation about the various format codes.
    """
    # XXX: use "caching" of lists with static strings (weekdays...)

    # allow format_X method names
    # pylint: disable-msg=C0103

    WEEKDAYS_ABBR = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'),
                     _('Sat'), _('Sun')]
    WEEKDAYS_FULL = [_('Monday'), _('Tuesday'), _('Wednesday'),
                     _('Thursday'), _('Friday'), _('Saturday'),
                     _('Sunday')]
    MONTHS_ABBR = [_('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May:abbr'),
                   _('Jun'), _('Jul'), _('Aug'), _('Sep'), _('Oct'),
                   _('Nov'), _('Dec')]
    MONTHS_FULL = [_('January'), _('February'), _('March'), _('April'),
                   _('May:full'), _('June'), _('July'), _('August'),
                   _('September'), _('October'), _('November'),
                   _('December')]

    def __init__(self, req, dateobj):
        self.req = req
        if isinstance(dateobj, datetime):
            self.date = dateobj
        elif isinstance(dateobj, int):
            self.date = datetime.utcfromtimestamp(dateobj)
        elif isinstance(dateobj, time.struct_time):
            self.date = datetime(dateobj[:7])
        elif dateobj is None:
            self.date = datetime(1, 1, 1)
        else:
            raise TypeError('%r is not a valid time object' % dateobj)

    def format(self, formatstring):
        bits = []
        for bit in split_format(formatstring):
            if bit.startswith('%'):
                handler = getattr(self, 'format_' + bit[1], None)
                if handler is not None:
                    bits.append(handler())
                else:
                    bits.append(bit)
            else:
                bits.append(bit)
        return u''.join(bits)

    def format_a(self):
        """abbreviated weekday name."""
        return self.req.gettext(self.WEEKDAYS_ABBR[self.date.weekday()])

    def format_A(self):
        """full weekday name."""
        return self.req.gettext(self.WEEKDAYS_FULL[self.date.weekday()])

    def format_b(self):
        """abbreviated month name."""
        return self.req.gettext(self.MONTHS_ABBR[self.date.month - 1])

    def format_B(self):
        """full month name."""
        return self.req.gettext(self.MONTHS_FULL[self.date.month - 1])

    def format_d(self):
        """Day of the month as a decimal number [01,31]."""
        return unicode(self.date.day)

    def format_H(self):
        """Hour (24-hour clock) as a decimal number [00,23]."""
        return unicode(self.date.hour)

    def format_I(self):
        """Hour (12-hour clock) as a decimal number [01,12]."""
        return unicode(self.date.hour % 12)

    def format_j(self):
        """Day of the year as a decimal number [001,366]."""
        return unicode(self.date.strftime('%j'))

    def format_J(self):
        """Day of the year as decimal number [1,366]."""
        return unicode(int(self.date.strftime('%j')))

    def format_m(self):
        """Month as a decimal number [01,12]."""
        return u'%02d' % self.date.month

    def format_n(self):
        """Month as a decimal number [1,12]."""
        return unicode(self.date.month)

    def format_M(self):
        """Minute as a decimal number [00,59]."""
        return u'%02d' % self.date.minute

    def format_N(self):
        """Minute as a decimal number [0,59]."""
        return unicode(self.date.minute)

    def format_p(self):
        """Locale's equivalent of either AM or PM."""
        _ = self.req.gettext
        if self.date.hour > 11:
            return _('PM')
        return _('AM')

    def format_P(self):
        """Locale's equivalent of either a.m. or p.m."""
        _ = self.req.gettext
        if self.date.hour > 11:
            return _('p.m.')
        return _('a.m.')

    def format_s(self):
        """Second as a decimal number [0,61]."""
        return unicode(self.date.second)

    def format_S(self):
        """Second as a decimal number [00,61]."""
        return u'%02d' % self.date.second

    def format_U(self):
        """Week number of the year (Sunday as the first day of the week)
        as a decimal number [00,53]. All days in a new year preceding the
        first Sunday are considered to be in week 0."""
        return unicode(self.date.strftime('%U'))

    def format_u(self):
        """Week number of the year (Sunday as the first day of the week)
        as a decimal number [0,53]. All days in a new year preceding the
        first Sunday are considered to be in week 0."""
        return unicode(int(self.date.strftime('%U')))

    def format_w(self):
        """Weekday as a decimal number [0(Sunday),6]."""
        return unicode(self.date.strftime('%w'))

    def format_z(self):
        """Weekday as a decimal number [0(Monday),6]."""
        #XXX: anyone something better than z?
        return unicode(self.date.weekday)

    def format_W(self):
        """Week number of the year (Monday as the first day of the week)
        as a decimal number [00,53]. All days in a new year preceding the
        first Monday are considered to be in week 0."""
        return unicode(self.date.strftime('%W'))

    def format_v(self):
        """Week number of the year (Monday as the first day of the week)
        as a decimal number [0,53]. All days in a new year preceding the
        first Monday are considered to be in week 0."""
        return unicode(int(self.date.strftime('%W')))

    def format_y(self):
        """Year without century as a decimal number [00,99]."""
        return unicode(self.date.strftime('%y'))

    def format_Y(self):
        """Year with century as a decimal number."""
        return unicode(self.date.year)

    def format_r(self):
        """English ordinal suffix for the day of the month, 2 characters;
        i.e. 'st', 'nd', 'rd' or 'th'"""
        _ = self.req.gettext
        if self.date.day in (11, 12, 13):
            return _('th')
        last = self.date.day % 10
        if last == 1:
            return _('st')
        if last == 2:
            return _('nd')
        if last == 3:
            return _('rd')
        return _('th')

    def format_t(self):
        """Number of days in the given month; i.e. '28' to '31'"""
        return '%02d' % monthrange(self.date.year, self.date.month)[1]

    def __repr__(self):
        return '<%s: [%s]>' % (
            self.__class__.__name__,
            ', '.join(str(i[7:]) for i in dir(self) if i.startswith('format_'))
        )


def format_timedelta(req, time1=None, time2=None):
    """
    Format the difference between two datetime or unix timestamp objects::

        >>> from pocoo.pkg.core.l10n import timedeltaformat
        >>> now = datetime.now()
        >>> timedeltaformat(req, now)
        u'6 seconds ago'
    """
    _ = req.gettext
    if time1 is None:
        time1 = datetime.utcnow()
    if isinstance(time1, datetime):
        time1 = time.mktime(time1.timetuple()) + time1.microsecond / 1e6
    if time2 is None:
        time2 = datetime.utcnow()
    if isinstance(time2, datetime):
        time2 = time.mktime(time2.timetuple()) + time2.microsecond / 1e6
    if time1 > time2:
        tmpl = _('%d %s in the future')
    else:
        tmpl = _('%d %s ago')
    def trans(s, entity):
        if entity == 's':
            e = _('second', 'seconds', s)
        elif entity == 'm':
            e = _('minute', 'minutes', s)
        elif entity == 'h':
            e = _('hour', 'hours', s)
        elif entity == 'd':
            e = _('day', 'days', s)
        elif entity == 'w':
            e = _('week', 'weeks', s)
        elif entity == 'M':
            e = _('month', 'months', s)
        else:
            e = _('year', 'years', s)
        return tmpl % (s, e)
    diff = abs(int(time2 - time1))
    for u, e in TIME_DELTA_UNITS:
        r = diff / float(u)
        if r >= 0.9:
            s = int(round(r))
            return trans(s, e)
    return trans(diff, 's')


def dateformat(date, context):
    #XXX: load default string from i10n language file
    req = context['REQUEST']
    formatstr = req.user.settings.get('dateformat')
    if formatstr is None:
        formatstr = req.ctx.cfg.get('general', 'dateformat',
                                    DEFAULT_DATE_FORMAT)
    f = DateFormatter(req, date or None)
    return f.format(formatstr)


def timeformat(date, context):
    #XXX: load default string from l10n language file
    req = context['REQUEST']
    formatstr = req.user.settings.get('timeformat')
    if formatstr is None:
        formatstr = req.ctx.cfg.get('general', 'timeformat',
                                    DEFAULT_TIME_FORMAT)
    f = DateFormatter(req, date or None)
    return f.format(formatstr)


def datetimeformat(date, context):
    #XXX: load default string from l10n language file
    req = context['REQUEST']
    formatstr = req.user.settings.get('datetimeformat')
    if formatstr is None:
        formatstr = req.ctx.cfg.get('general', 'datetimeformat',
                                    DEFAULT_DATETIME_FORMAT)
    f = DateFormatter(req, date or None)
    return f.format(formatstr)


def timedeltaformat(date, context, obj2=None):
    req = context['REQUEST']
    return format_timedelta(req, date or None, obj2 or None)
