# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.user
    ~~~~~~~~~~~~~~~~~~~

    User model and utilities.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from os import path
from datetime import datetime
from pocoo.db import meta, DatabaseModel, lazy_column
from pocoo.http import DirectResponse, AccessDeniedResponse
from pocoo.application import LinkableMixin
from pocoo.utils.text import gen_password, gen_activation_key, gen_pwhash, \
     check_pwhash
from pocoo.utils.uri import urlencode

from pocoo.pkg.core.db import users, groups, posts, group_members


def get_all_usernames(ctx):
    """Return a list of all usernames."""
    result = ctx.engine.execute(meta.select([users.c.username]))
    return [row[0] for row in result]


def get_id_username_mapping(ctx):
    """Return a ``user_id`` -> ``username`` mapping."""
    result = ctx.engine.execute(meta.select([users.c.user_id, users.c.username]))
    return dict(tuple(row) for row in result)


def get_user_list(ctx, order_by=users.c.username, order='asc', letter=None,
                  hide_internal=False):
    """Return a list of all users with public details."""
    #XXX: sorting with databases sucks :-/ if sorted by username, resort
    #     with python, and btw, this is ugly
    u = users.c
    q = []
    if letter:
        q.append(u.username.startswith(letter))
    if hide_internal:
        q.append((u.username != 'default') & (u.username != 'anonymous'))
    try:
        order = {
            'desc':     meta.desc,
            'asc':      meta.asc
        }[order]
    except KeyError:
        raise ValueError('order must be either \'asc\' or \'desc\'')
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


def get_all_groupnames(ctx):
    """Return a list of groupnames."""
    result = ctx.engine.execute(meta.select([groups.c.name]))
    return [row[0] for row in result]


def get_id_groupname_mapping(ctx):
    """Return a group_id -> groupname mapping."""
    result = ctx.engine.execute(meta.select([groups.c.group_id, groups.c.name]))
    return dict(tuple(row) for row in result)


def get_group_list(ctx, order_by=groups.c.name, order='asc', letter=None,
                   show_hidden=True):
    """Return a list of all groups with public details."""
    g = groups.c
    q = []
    if letter:
        q.append(g.name.startswith(letter))
    if not show_hidden:
        q.append(g.hidden == True)
    try:
        order = {
            'desc':     meta.desc,
            'asc':  meta.asc
        }[order]
    except KeyError:
        raise ValueError('order must be either \'asc\' or \'desc\'')
    result = ctx.engine.execute(meta.select([g.group_id, g.name, g.public,
                                             g.hidden], meta.and_(*q),
                                        order_by=[order(order_by)]))
    def prepare(row):
        d = dict(row)
        d['url'] = ctx.make_url('groups', urlencode(row['name']))
        return d
    return [prepare(row) for row in result]


def get_user(req, user_id_or_name):
    """
    Return a dict of user information for the template.
    """
    ctx = req.ctx
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
        # XXX: error return needed
        return
    user = dict(row)
    user['url'] = ctx.make_url('users', urlencode(row['username']))
    return user


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


def get_id_by_name(ctx, name):
    u = users.c
    result = ctx.engine.execute(meta.select([u.user_id],
                                       u.username == name))
    row = result.fetchone()
    if not row:
        raise UserNotFound
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
    pass


class User(DatabaseModel, LinkableMixin):
    NotFound = UserNotFound

    def __init__(self, ctx, user_id):
        self.ctx = ctx
        self.user_id = user_id
        super(User, self).__init__(ctx, users, 'user_id')

        from pocoo.pkg.core.acl import AclManager
        self.acl = AclManager(ctx, self)

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
    read_threads = lazy_column('read_threads')
    read_posts = lazy_column('read_posts')

    @property
    def relative_url(self):
        return 'users/%s' % self.username

    @staticmethod
    def create(ctx, username, password, email, activate=False):
        """Creates a new user."""
        if activate:
            act_key = gen_activation_key()
        else:
            act_key = None
        result = ctx.engine.execute(users.insert(),
            username=username,
            email=email,
            act_key=act_key,
            pwhash=gen_pwhash(password),
            register_date=datetime.utcnow(),
            post_count=0
        )
        return User(ctx, result.last_inserted_ids()[0])

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

    def iter_groups(self):
        """
        Return a generator for all groups this user has joined.
        """
        result = self.ctx.engine.execute(meta.select([groups.c.group_id],
            (users.c.user_id == self.user_id) &
            (group_members.c.group_id == groups.c.group_id) &
            (group_members.c.user_id == users.c.user_id)
        ))
        for row in result:
            yield Group(self.ctx, row[0])

    def activate(self):
        self.act_key = None

    def deactivate(self):
        self.act_key = gen_activation_key()

    @property
    def identified(self):
        return self.user_id > 0

    @property
    def active(self):
        return not self.act_key

    @property
    def groups(self):
        return list(self.iter_groups())

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


class GroupNotFound(Exception):
    pass


class Group(DatabaseModel):

    def __init__(self, ctx, group_id):
        self.ctx = ctx
        self.group_id = group_id
        super(Group, self).__init__(ctx, groups, 'group_id')

        from pocoo.pkg.core.acl import AclManager
        self.acl = AclManager(ctx, self)

    subject_id = lazy_column('subject_id')
    name = lazy_column('name')
    public = lazy_column('public')
    hidden = lazy_column('hidden')

    @staticmethod
    def create(ctx, name, public=True, hidden=False):
        """Create a new usergroup."""
        result = ctx.engine.execute(groups.insert(),
            name=name,
            public=public,
            hidden=hidden
        )
        return Group(ctx, result.last_inserted_ids()[0])

    @property
    def members(self):
        return list(self.iter_members())

    def iter_members(self):
        """Return a generator for all group members."""
        result = self.ctx.engine.execute(meta.select([users.c.user_id],
            (groups.c.group_id == self.group_id) &
            (group_members.c.group_id == groups.c.group_id) &
            (group_members.c.user_id == users.c.user_id)
        ))
        for row in result:
            yield User(self.ctx, row[0])

    def add_member(self, user):
        """Add a new member to the group."""
        if isinstance(user, User):
            user_id = user.user_id
        else:
            user_id = User(self.ctx, user).user_id
        # check if the user is already a member of the group
        result = self.ctx.engine.execute(meta.select([group_members.c.user_id],
            (group_members.c.user_id == user_id) &
            (group_members.c.group_id == self.group_id)
        ))
        if result.fetchone() is not None:
            raise ValueError('The user %d is alreay a member of this group' %
                             user_id)
        self.ctx.engine.execute(group_members.insert(),
            user_id = user_id,
            group_id = self.group_id
        )

    def remove_member(self, user):
        """Remove a member from the group."""
        if isinstance(user, User):
            user_id = user.user_id
        else:
            user_id = User(self.ctx, user).user_id
        # check if the user is not in the group
        result = self.ctx.engine.execute(meta.select([group_members.c.user_id],
            (group_members.c.user_id == user_id) &
            (group_members.c.group_id == self.group_id)
        ))
        if result.fetchone() is None:
            raise ValueError('The user %d is not a member of this group' %
                             user_id)
        self.ctx.engine.execute(group_members.delete(
            (group_members.c.group_id == self.group_id) &
            (group_members.c.user_id == user_id)
        ))

    def is_member(self, user):
        """Check if a user is a member of this group."""
        if isinstance(user, User):
            user_id = user.user_id
        else:
            user_id = User(self.ctx, user).user_id
        result = self.ctx.engine.execute(meta.select([group_members.c.user_id],
            (group_members.c.user_id == user_id) &
            (group_members.c.group_id == self.group_id)
        ))
        return result.fetchone() is not None

    def __eq__(self, other):
        return self.group_id == other.group_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %d: %r>' % (
            self.__class__.__name__,
            self.group_id,
            self.name
        )
