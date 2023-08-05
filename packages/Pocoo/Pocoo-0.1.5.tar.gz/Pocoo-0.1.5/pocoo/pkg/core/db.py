# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.db
    ~~~~~~~~~~~~~~~~~

    Pocoo core database definition.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.db import meta, DatabaseObserver


#: fake translator function
_ = lambda x: x

#: user id of the anonymous user.
ANONYMOUS_USER_ID = 1
ANONYMOUS_USERNAME = 'anonymous'

#: group id and name of the everybody group.
EVERYBODY_GROUP_ID = 1
EVERYBODY_GROUP_NAME = _('Everybody')

#: group id and name of the group for registered users
REGISTERED_GROUP_ID = 2
REGISTERED_GROUP_NAME = _('Registered users')


#: session table
#: ^^^^^^^^^^^^^
#: stores the session data for all users, either logged in or
#: logged out. It knows about the last reload time, current
#: session data in form of a pickled dict, the time of expiration,
#: current ip address and of course the session id.
sessions = meta.Table('core_sessions',
    meta.Column('session_key', meta.Unicode(40), primary_key=True),
    meta.Column('ip_addr', meta.Unicode(15)),
    meta.Column('expires', meta.DateTime),
    meta.Column('last_reload', meta.DateTime),
    meta.Column('data', meta.Pickled(dict)),
    meta.Column('action', meta.Unicode)
)

#: user table
#: ^^^^^^^^^^
#: the user table stores all relevant information for a
#: registered user.
users = meta.Table('core_users',
    meta.Column('user_id', meta.Integer, primary_key=True),
    meta.Column('username', meta.Unicode(40)),
    meta.Column('email', meta.Unicode(250)),
    meta.Column('pwhash', meta.Unicode(60)),
    meta.Column('act_key', meta.Unicode(8)),
    meta.Column('language', meta.Unicode(2)),
    meta.Column('profile', meta.Pickled(dict)),
    meta.Column('settings', meta.Pickled(dict)),
    meta.Column('last_login', meta.DateTime),
    meta.Column('register_date', meta.DateTime),
    meta.Column('post_count', meta.Integer),
    meta.Column('acl_rules', meta.Binary),
    meta.Column('status_tracker_data', meta.Binary)
)

#: group table
#: ^^^^^^^^^^^
#: stores groups. Just the name, id of the group and optionally
#: an item_id which is used to specify acl rules on it.
#: if internationalize is True the group_name and description
#: will be translated by gettext for the user. (used by default
#: system groups for example).
groups = meta.Table('core_groups',
    meta.Column('group_id', meta.Integer, primary_key=True),
    meta.Column('group_name', meta.Unicode(40)),
    meta.Column('description', meta.Unicode),
    meta.Column('internationalize', meta.Boolean, nullable=False),
    meta.Column('acl_rules', meta.Binary)
)

#: group member table
#: ^^^^^^^^^^^^^^^^^^
#: used to declare a user as member of a group. If `is_leader`
#: is true the user will be able to administrate the group.
#: this isn't done using acls because it's also a visible detail
#: on the group page.
group_members = meta.Table('core_group_members',
    meta.Column('user_id', meta.Integer,
                meta.ForeignKey('core_users.user_id')),
    meta.Column('group_id', meta.Integer,
                meta.ForeignKey('core_groups.group_id')),
    meta.Column('is_leader', meta.Boolean)
)

#: forum table
#: ^^^^^^^^^^^
#: stores a forum. A forum can have a parent or no parent if it's
#: a category on the main page, it could have a item_id which is
#: used in acl rules.
#: `position` is an optional column for sorting. The higher the
#: value the more on the bottom of the page the forum will appear.
#: the second parameter for sorting is the forum_id.
#: `link` could be `NULL` or an URL, if set the forum works as
#: redirect to an external resource.
#:
#: `post_count` and `thread_count` held the cached value of the
#: current post and thread count in the forum and all sub forums.
#: additionally the `local_thread_count` only counts the number
#: of threads directly in this forum without subforums. It's used
#: for example for builing the pagination.
forums = meta.Table('core_forums',
    meta.Column('forum_id', meta.Integer, primary_key=True),
    meta.Column('parent_id', meta.Integer,
                meta.ForeignKey('core_forums.forum_id')),
    meta.Column('name', meta.Unicode(100)),
    meta.Column('description', meta.Unicode),
    meta.Column('position', meta.Integer),
    meta.Column('link', meta.Unicode(200)),
    #XXX: foreign key doesn't work
    meta.Column('last_post_id', meta.Integer),
    meta.Column('post_count', meta.Integer),
    meta.Column('thread_count', meta.Integer),
    meta.Column('local_thread_count', meta.Integer)
)

#: post table
#: ^^^^^^^^^^
#: stores threads and posts. A thread isn't more than just a post
#: which `root_post_id` is the same as its own `post_id`. It lives
#: in the forum called `forum_id`, and knows about it's `post_count`,
#: `view_count`, `author_id` and `timestamp`.
#: additionally it stores the `username` (for anonymous posters),
#: `title`, `text` and `parsed_text`. The latter three values could
#: probably move into their own table `core_post_texts` somewhere in
#: the future.
posts = meta.Table('core_posts',
    meta.Column('post_id', meta.Integer, primary_key=True),
    meta.Column('forum_id', meta.Integer,
                meta.ForeignKey('core_forums.forum_id')),
    meta.Column('parent_id', meta.Integer,
                meta.ForeignKey('core_posts.post_id')),
    meta.Column('root_post_id', meta.Integer,
                meta.ForeignKey('core_posts.post_id')),
    meta.Column('post_count', meta.Integer),
    meta.Column('view_count', meta.Integer),
    meta.Column('author_id', meta.Integer,
                meta.ForeignKey('core_users.user_id')),
    meta.Column('username', meta.Unicode(200)),
    meta.Column('title', meta.Unicode(200)),
    meta.Column('text', meta.Unicode),
    meta.Column('parsed_text', meta.Binary),
    meta.Column('deleted', meta.Boolean, nullable=False),
    meta.Column('locked', meta.Boolean, nullable=False),
    meta.Column('timestamp', meta.DateTime)
)


#: privilege table
#: ^^^^^^^^^^^^^^^^
#: gives the acl privilege names unique ids used in the
#: binary acl mapping.
privileges = meta.Table('core_privileges',
    meta.Column('privilege_id', meta.Integer, primary_key=True),
    meta.Column('privilege_name', meta.Unicode(40))
)


class CoreTableObserver(DatabaseObserver):
    """
    The default table observer. Insert default values like
    anonymous user and the default `ACL_TYPES`
    """

    def after_table_creation(self, table):
        e = self.ctx.engine.execute
        if table is users:
            e(users.insert(),
                user_id=ANONYMOUS_USER_ID,
                username=ANONYMOUS_USERNAME,
                email=None,
                password=None,
                activate=False
            )
        elif table is groups:
            from pocoo.pkg.core.user import Group
            from pocoo.pkg.core.acl import Permission

            g = Group.create(self.ctx, EVERYBODY_GROUP_NAME, u'',
                             EVERYBODY_GROUP_ID, True)
            g.acl.set_site_privilege('READ_POST', Permission.allow)
            g.add_member(ANONYMOUS_USER_ID)
            g.save()

            g = Group.create(self.ctx, REGISTERED_GROUP_NAME, u'',
                             REGISTERED_GROUP_ID, True)
            g.acl.set_site_privilege('CREATE_THREAD', Permission.allow)
            g.acl.set_site_privilege('REPLY_POST', Permission.allow)
            g.save()
