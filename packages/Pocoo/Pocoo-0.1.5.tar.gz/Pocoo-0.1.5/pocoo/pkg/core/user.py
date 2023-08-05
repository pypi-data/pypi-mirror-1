# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.user
    ~~~~~~~~~~~~~~~~~~~

    User/Group model and utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from os import path
from datetime import datetime
from pocoo.db import meta, DatabaseModel, lazy_column, \
     get_column_value, set_column_value
from pocoo.http import DirectResponse, AccessDeniedResponse
from pocoo.application import LinkableMixin
from pocoo.utils.text import gen_password, gen_activation_key, gen_pwhash, \
     check_pwhash
from pocoo.utils.uri import urlencode
from pocoo.pkg.core.db import users, groups, group_members, posts, \
     ANONYMOUS_USER_ID, EVERYBODY_GROUP_ID, REGISTERED_GROUP_ID
from pocoo.pkg.core.acl import UserAclManager, GroupAclManager


def get_all_usernames(ctx):
    """Return a list of all usernames."""
    result = ctx.engine.execute(meta.select([users.c.username],
        order_by=[meta.asc(users.c.username)]))
    return [row[0] for row in result]


def get_all_groups(ctx):
    """Return a list of all group names."""
    result = ctx.engine.execute(meta.select([groups.c.group_name],
        order_by=[meta.asc(users.c.group_name)]))
    return [row[0] for row in result]


def get_user_list(ctx, order_by='username', order='asc', letter=None,
                  hide_internal=False):
    """Return a list of all users with public details."""
    #XXX: sorting with databases sucks :-/ if sorted by username, resort
    #     with python, and btw, this is ugly
    u = users.c
    q = []
    if letter:
        q.append(u.username.startswith(letter))
    if hide_internal:
        q.append((u.user_id != ANONYMOUS_USER_ID))
    try:
        order = {
            'desc':     meta.desc,
            'asc':      meta.asc
        }[order]
    except KeyError:
        raise ValueError('order must be either \'asc\' or \'desc\'')
    try:
        order_by = u[order_by]
    except KeyError:
        raise ValueError('unknown column %r' % order_by)
    result = ctx.engine.execute(meta.select([u.user_id, u.username, u.email,
                                             u.profile, u.last_login,
                                        u.register_date, u.post_count],
                                        meta.and_(*q),
                                        order_by=[order(order_by)]))
    def prepare(row):
        d = dict(row)
        d['url'] = ctx.make_url('users', urlencode(row['username']))
        return d
    return [prepare(row) for row in result]


def get_group_list(ctx, order_by='group_name', order='asc', letter=None):
    """Return a list of all groups."""
    g = groups.c
    q = None
    if letter:
        q = g.startswith(letter)
    try:
        order = {
            'desc':     meta.desc,
            'asc':      meta.asc
        }[order]
    except KeyError:
        raise ValueError('order must be either \'asc\' or \'desc\'')
    try:
        order_by = g[order_by]
    except KeyError:
        raise ValueError('unknown column %r' % order_by)
    result = ctx.engine.execute(meta.select([g.group_id, g.group_name,
                                             g.description], q,
                                             order_by=[order(order_by)]))
    def prepare(row):
        d = dict(row)
        d['url'] = ctx.make_url('groups', urlencode(row['group_name']))
        return d
    return [prepare(row) for row in result]


def get_user(ctx, user_id_or_name):
    """
    Return a dict of user information for the template.
    Raise `UserNotFound` if the user does not exist.
    """
    u = users.c
    if isinstance(user_id_or_name, (int, long)):
        q = (u.user_id == user_id_or_name)
    else:
        q = (u.username == user_id_or_name)
    result = ctx.engine.execute(meta.select([u.user_id, u.username, u.email,
                                             u.profile, u.settings, u.last_login,
                                             u.register_date, u.post_count], q))
    row = result.fetchone()
    if row is None:
        raise UserNotFound()
    user = dict(row)
    user['url'] = ctx.make_url('users', urlencode(row['username']))
    return user


def get_group(ctx, group_id_or_name):
    """
    Return a dict of group information for the table.
    Raise `GroupNotFound` if the group does not exist.
    """
    ctx = req.ctx
    g = groups.c
    if isinstance(group_id_or_name, (int, long)):
        q = (u.group_id == group_id_or_name)
    else:
        q = (g.group_name == group_id_or_name)
    row = ctx.engine.execute(meta.select([g.group_id, g.group_name,
                                          g.description], q)).fetchone()
    if row is None:
        raise GroupNotFound()
    group = dcit(row)
    group['url'] = ctx.make_url('groups', urlencode(row['group_name']))
    return group


def get_user_avatar(req, user_id_or_name):
    """
    Return the user avatar.
    """
    if isinstance(user_id_or_name, (int, long)):
        q = (users.c.user_id == user_id_or_name)
    else:
        q = (users.c.username == user_id_or_name)
    result = req.ctx.engine.execute(meta.select([users.c.user_id], q))
    row = result.fetchone()
    if row is not None:
        fn = path.join(req.ctx.cfg.root, 'avatars', '%d.png' % row[0])
        if path.exists(fn):
            f = file(fn, 'rb')
            result = f.read()
            f.close()
            return result


def get_userid_by_name(ctx, name):
    """
    Return the user id of a give username.
    Raise `UserNotFound` if the user does not exist.
    """
    row = ctx.engine.execute(meta.select([users.c.user_id],
        users.c.username == name
    )).fetchone()
    if not row:
        raise UserNotFound()
    return row[0]

def get_groupid_by_name(ctx, name):
    """
    Return the group id of a given groupname.
    Raise `GroupNotFound` if the group does not exist.
    """
    row = ctx.engine.execute(meta.select([groups.c.group_id],
        groups.c.group_name == name
    )).fetchone()
    if not row:
        raise GroupNotFound()
    return row[0]


def check_login_data(ctx, username, password):
    """
    Check if a username and password was found in the
    database. Returns None if the user does not exist
    or the password is incorrect, otherwise it returns
    the user id.
    """
    u = users.c
    result = ctx.engine.execute(meta.select([u.user_id, u.pwhash, u.act_key],
        users.c.username == username
    ))
    row = result.fetchone()
    if row is not None and not row['act_key'] and \
       check_pwhash(row['pwhash'], password):
        return row['user_id']


def sync_post_count(ctx, user_id):
    """Sync the user post count with the post tables."""
    def do(con):
        result = con.execute(meta.select([meta.func.count(posts.c.post_id)],
            posts.c.author_id == user_id
        ))
        con.execute(users.update(users.c.user_id == user_id),
            post_count = result.fetchone()[0]
        )
    ctx.engine.transaction(do)


def reset_password(ctx, username, email):
    """
    Reset the password and returns the new password
    if the email matched the username.
    If not it will return None.
    """
    password = gen_password()
    result = ctx.engine.execute(users.update((users.c.username == username) &
                                        (users.c.email == email)),
        pwhash = gen_pwhash(password)
    )
    if result.rowcount:
        return password


class UserNotFound(Exception):
    """Raise if a user does not exist."""


class GroupNotFound(Exception):
    """Raise if a group does not exist."""


class User(DatabaseModel, LinkableMixin):
    """
    Represents a user object for manipulating it. It's also used
    by the auth system to bind auth information to the request
    object.
    """

    def __init__(self, ctx, user_id):
        self.ctx = ctx
        self.user_id = user_id
        super(User, self).__init__(ctx, users, 'user_id')

        self.acl = UserAclManager(
            ctx, self.user_id, lambda: get_column_value(self, 'acl_rules')
        )

    subject_id = lazy_column('subject_id')
    username = lazy_column('username')
    email = lazy_column('email')
    pwhash = lazy_column('pwhash')
    act_key = lazy_column('act_key')
    language = lazy_column('language')
    profile = lazy_column('profile')
    settings = lazy_column('settings')
    last_login = lazy_column('last_login')
    register_date = lazy_column('register_date')
    post_count = lazy_column('post_count')

    @property
    def relative_url(self):
        return 'users/%s' % self.username

    @staticmethod
    def create(ctx, username, password, email, activate=False,
               no_membership=False):
        """
        Create a new user. If you set `no_membership` to `False`
        the newly created user won't be a member of the two
        default groups for registered users, ``everybody`` and
        ``registered users``.
        """
        optional = {}
        if activate:
            optional['act_key'] = gen_activation_key()
        if password is not None:
            optional['pwhash'] = gen_pwhash(password)
        def do(con):
            result = con.execute(users.insert(),
                username=username,
                email=email,
                register_date=datetime.utcnow(),
                post_count=0,
                **optional
            )
            user_id = result.last_inserted_ids()[0]
            if not no_membership:
                for group_id in EVERYBODY_GROUP_ID, REGISTERED_GROUP_ID:
                    con.execute(group_members.insert(),
                        user_id=user_id,
                        group_id=group_id,
                        is_leader=False
                    )
            return user_id
        return User(ctx, ctx.engine.transaction(do))

    @staticmethod
    def by_name(ctx, username):
        return User(ctx, get_userid_by_name(ctx, username))

    def save(self, con=None):
        set_column_value(self, 'acl_rules', self.acl.dump())
        super(User, self).save(con)

    def check_password(self, password):
        if not self.exists:
            return False
        return check_pwhash(self.pwhash, password)

    def set_password(self, password):
        self.pwhash = gen_pwhash(password)

    def assert_logged_in(self):
        """
        Check if the user is logged in and raise a DirectResponse
        exception with an AccessDeniedResponse to display the user a
        login or "missing permission" page.
        """
        if not self.identified:
            raise DirectResponse(AccessDeniedResponse())

    def activate(self):
        self.act_key = None

    def deactivate(self):
        self.act_key = gen_activation_key()

    def iter_groups(self):
        result = self.ctx.engine.execute(group_members.select(
            group_members.c.user_id == self.user_id
        ))
        for row in result:
            yield Group(self.ctx, row.group_id)

    @property
    def identified(self):
        return self.user_id != ANONYMOUS_USER_ID

    @property
    def active(self):
        return not self.act_key

    @property
    def groups(self):
        return list(self.iter_groups())

    @property
    def admin(self):
        return self.acl.can_access_site('BOARD_ADMIN')

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %d: %r>' % (
            self.__class__.__name__,
            self.user_id,
            self.username
        )


class Group(DatabaseModel):
    """
    Represents a group. This class exists for manipulating groups
    and group access rules. Don't pass it to templates, for
    retrieving data for templates have a look at the utility
    functions in this module.

    Members of groups automatically inherit the group acl rules.
    """

    def __init__(self, ctx, group_id):
        self.ctx = ctx
        self.group_id = group_id
        super(Group, self).__init__(ctx, groups, 'group_id')

        self.acl = GroupAclManager(
            ctx, self.group_id, lambda: get_column_value(self, 'acl_rules')
        )

    group_name = lazy_column('group_name')
    description = lazy_column('description')
    internationalize = lazy_column('internationalize')

    @staticmethod
    def create(ctx, group_name, description=u'', group_id=None,
               internationalize=False):
        optional = {}
        if group_id is not None:
            optional['group_id'] = group_id
        return Group(ctx, ctx.engine.execute(groups.insert(),
            group_name=group_name,
            description=description,
            internationalize=internationalize,
            **optional
        ).last_inserted_ids()[0])

    @staticmethod
    def by_name(ctx, group_name):
        return Group(ctx, get_groupid_by_name(ctx, group_name))

    def save(self, con=None):
        set_column_value(self, 'acl_rules', self.acl.dump())
        super(Group, self).save(con)

    def add_member(self, user, is_leader=False):
        """Add a new member to the list."""
        if isinstance(user, User):
            user = user.user_id
        def do(con):
            query = (
                (group_members.c.group_id == self.group_id) &
                (group_members.c.user_id == user)
            )
            row = con.execute(meta.select([group_members.c.is_leader],
                                          query)).fetchone()
            if row:
                if row[0] == is_leader:
                    return
                con.execute(group_members.update(query),
                    is_leader=is_leader
                )
            else:
                con.execute(group_members.insert(),
                    group_id=self.group_id,
                    user_id=user,
                    is_leader=is_leader
                )
        self.ctx.engine.transaction(do)

    def add_leader(self, user):
        """Add a new leader to the group. If the new leader is
        already a member the status will get updated."""
        return self.add_member(user, True)

    def remove_member(self, user):
        """Remove a member from the group. If the member was a
        leader he will be removed nevertheless."""
        if isinstance(user, User):
            user = user.user_id
        self.ctx.engine.execute(group_members.delete(
            (group_members.c.group_id == self.group_id) &
            (group_members.c.user_id == user)
        ))

    def iter_members(self):
        result = self.ctx.engine.execute(group_members.select(
            group_members.c.group_id == self.group_id
        ))
        for row in result:
            yield User(row.user_id)

    @property
    def members(self):
        return list(self.iter_members())

    def __eq__(self, other):
        return self.group_id == other.group_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %d: %r>' % (
            self.__class__.__name__,
            self.group_id,
            self.group_name
        )
