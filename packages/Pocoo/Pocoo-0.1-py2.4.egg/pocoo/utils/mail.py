# -*- coding: utf-8 -*-
"""
    pocoo.utils.mail
    ~~~~~~~~~~~~~~~~

    Pocoo mail sending utils.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import urlparse
from smtplib import SMTP, SMTPException
from email.MIMEText import MIMEText

from pocoo.exceptions import PocooRuntimeError, EmailSMTPError


class Email(object):
    """
    Represents one E-Mail message that can be sent.
    """

    def __init__(self, ctx, subject=None, to_addrs=None, text=None):
        self.ctx = ctx
        self.subject = u' '.join(subject.splitlines())
        self.text = text
        self.from_addr = ctx.cfg.get('email', 'from', None)
        if not self.from_addr:
            p = urlparse.urlparse(ctx.cfg.get('general', 'serverpath'))
            self.from_addr = '%s <noreply@%s>' % (
                ctx.cfg.get('board', 'title'),
                p[1].split(':')[0]
            )
        self.to_addrs = []
        if isinstance(to_addrs, basestring):
            self.add_addr(to_addrs)
        else:
            for addr in to_addrs:
                self.add_addr(addr)

    def add_addr(self, addr):
        """
        Add an mail address to the list of recipients
        """
        lines = addr.splitlines()
        if len(lines) != 1:
            raise ValueError('invalid value for email address')
        self.to_addrs.append(lines[0])

    def send(self):
        """
        Send the message.
        """
        if not self.subject or not self.text or not self.to_addrs:
            raise PocooRuntimeError("Not all mailing parameters filled in")
        try:
            smtp = SMTP(self.ctx.cfg.get('email', 'host', 'localhost'))
        except SMTPException, e:
            raise EmailSMTPError(str(e))

        if self.ctx.cfg.get('email', 'user', ''):
            try:
                try:
                    smtp.login(self.ctx.cfg.get('email', 'user'),
                               self.ctx.cfg.get('email', 'pass', ''))
                except SMTPException:
                    raise EmailSMTPError(str(e))
            finally:
                smtp.quit()

        prefix = self.ctx.cfg.get('email', 'prefix', '')
        suffix = self.ctx.cfg.get('email', 'suffix', '')

        msg = MIMEText(self.text)
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(self.to_addrs)
        msg['Subject'] = prefix + self.subject + suffix

        try:
            try:
                ret = smtp.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            except SMTPException:
                return EmailSMTPError(str(e))
        finally:
            smtp.quit()

        return ret

    def send_quiet(self):
        """
        Send the message, swallowing exceptions.
        """
        try:
            return self.send()
        except Exception:
            return False
