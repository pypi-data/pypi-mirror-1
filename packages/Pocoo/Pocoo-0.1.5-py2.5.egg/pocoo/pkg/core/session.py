# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.session
    ~~~~~~~~~~~~~~~~~~~~~~

    Pocoo session handling.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

import md5
import time
import random

from datetime import datetime, timedelta
from pocoo.application import RequestWrapper
from pocoo.settings import cfg
from pocoo.db import meta
from pocoo.utils.uri import urlencode
from pocoo.pkg.core.db import sessions, users
from pocoo.pkg.core.auth import get_auth_provider


def get_active_sessions(ctx, delta=timedelta(minutes=5)):
    """
    Return a tuple in the following form::

        (sessions, user_count, guest_count, total)

    sessions is a dict for the template with all relevant
    information about the sessions, user_count is the
    amount of all logged in users, guest_count is the
    amount of all anonymous users and total is the total
    number of all sessions being active.
    """
    provider = get_auth_provider(ctx)
    now = datetime.utcnow()
    def do(con):
        session_list = []
        user_count = 0
        guest_count = 0
        r = con.execute(sessions.select(
            sessions.c.last_reload > now - delta
        ))
        while True:
            row = r.fetchone()
            if row is None:
                break
            user = con.execute(meta.select([users.c.user_id, users.c.username],
                users.c.user_id == provider.get_user_id(row['data'])
            )).fetchone()
            if user is None or user['user_id'] < 1:
                guest_count += 1
                user_data = None
            else:
                user_data = {
                    'username':     user['username'],
                    'user_id':      user['user_id'],
                    'url':      ctx.make_url('users', urlencode(user['username'])),
                }
                user_count += 1
            session_list.append({
                'last_reload':      row['last_reload'],
                'user':             user_data
            })
        session_list.sort(key=lambda x: x['last_reload'])
        return session_list, user_count, guest_count, user_count + guest_count
    return ctx.engine.transaction(do)


class Session(dict):
    """Session Model"""

    def __init__(self, ctx, sid, ip):
        self.ctx = ctx
        r = ctx.engine.execute(sessions.select(
            (sessions.c.session_key == sid) &
            (sessions.c.ip_addr == ip) &
            (sessions.c.expires >= datetime.utcnow())
        ))
        data = r.fetchone()
        if data is None:
            super(Session, self).__init__()
            self.sid = None
        else:
            super(Session, self).__init__(data['data'])
            self.sid = sid
        self.ip = ip

    def __hash__(self):
        return hash(self.sid)

    def to_dict(self):
        """Return the session data as normal dict."""
        return dict(self)

    def save(self, cookie_expire):
        """Save changes back to the database and updates
        expires and last_reload. Returns a datetime object
        with the time of the session expire."""
        now = datetime.utcnow()
        expires = now + timedelta(seconds=cookie_expire)
        if not self.sid:
            while True:
                hashval = md5.new('%s|%s' % (random.random(), time.time()))
                sid = hashval.hexdigest()
                r = self.ctx.engine.execute(sessions.select(
                    sessions.c.session_key == sid
                ))
                if r.fetchone() is None:
                    break
            self.sid = sid
            self.ctx.engine.execute(sessions.insert(),
                session_key = self.sid,
                ip_addr = self.ip,
                expires = expires,
                last_reload = now,
                data = self.to_dict()
            )
        else:
            q = sessions.c.session_key == self.sid
            self.ctx.engine.execute(sessions.update(q),
                expires = expires,
                last_reload = now,
                data = self.to_dict()
            )
        return expires

    def __repr__(self):
        return '<%s %s: %r>' % (
            self.__class__.__name__,
            self.sid,
            dict.__repr__(self)
        )


class SessionWrapper(RequestWrapper):
    """
    SessionWrapper loads/stores request.session.
    """
    cookie_name = cfg.str('board', 'cookiename', 'SESSION')
    cookie_expires = cfg.int('board', 'cookieexpires', 7200)

    def get_priority(self):
        # request.session should be set before anything else,
        # but after a possible caching system.
        return 2

    def process_request(self, req):
        cookie = req.cookies.get(self.cookie_name, None)
        sid = cookie and cookie.value or None
        ip = req.environ['REMOTE_ADDR']
        req.session = Session(self.ctx, sid, ip)

    def process_response(self, req, resp):
        expires = req.session.save(self.cookie_expires)
        resp.set_cookie(str(self.cookie_name), req.session.sid,
                        max_age=self.cookie_expires, expires=expires)
        return resp
