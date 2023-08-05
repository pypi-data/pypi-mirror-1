# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.db
    ~~~~~~~~~~~~~~~~~

    Pocoo core database definition.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.db import meta, DatabaseObserver


ANONYMOUS_USER_ID = -1
DEFAULT_USER_ID = 0


sessions = meta.Table('core_sessions',
    meta.Column('session_key', meta.Unicode(40), primary_key=True),
    meta.Column('ip_addr', meta.Unicode(15)),
    meta.Column('expires', meta.DateTime),
    meta.Column('last_reload', meta.DateTime),
    meta.Column('data', meta.Pickled(dict)),
)

users = meta.Table('core_users',
    meta.Column('user_id', meta.Integer, primary_key=True),
    meta.Column('subject_id', meta.Integer,
                meta.ForeignKey('core_acl_subjects.subject_id')),
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
    meta.Column('read_threads', meta.Binary),
    meta.Column('read_posts', meta.Binary),
)

groups = meta.Table('core_groups',
    meta.Column('group_id', meta.Integer, primary_key=True),
    meta.Column('subject_id', meta.Integer,
                meta.ForeignKey('core_acl_subjects.subject_id')),
    meta.Column('name', meta.Unicode(40)),
    meta.Column('public', meta.Boolean),
    meta.Column('hidden', meta.Boolean)
)

group_members = meta.Table('core_group_members',
    meta.Column('user_id', meta.Integer,
                meta.ForeignKey('core_users.user_id')),
    meta.Column('group_id', meta.Integer,
                meta.ForeignKey('core_groups.group_id'))
)

forums = meta.Table('core_forums',
    meta.Column('forum_id', meta.Integer, primary_key=True),
    meta.Column('parent_id', meta.Integer,
                meta.ForeignKey('core_forums.forum_id')),
    meta.Column('object_id', meta.Integer,
                meta.ForeignKey('core_acl_objects.object_id')),
    meta.Column('name', meta.Unicode(100)),
    meta.Column('description', meta.Unicode),
    meta.Column('position', meta.Integer),
    meta.Column('link', meta.Unicode(100)),
    #XXX: foreign key doesn't work
    meta.Column('last_post_id', meta.Integer),
    meta.Column('post_count', meta.Integer),
    meta.Column('thread_count', meta.Integer)
)

posts = meta.Table('core_posts',
    meta.Column('post_id', meta.Integer, primary_key=True),
    meta.Column('forum_id', meta.Integer,
                meta.ForeignKey('core_forums.forum_id')),
    meta.Column('parent_id', meta.Integer,
                meta.ForeignKey('core_posts.post_id')),
    meta.Column('root_post_id', meta.Integer,
                meta.ForeignKey('core_posts.post_id')),
    meta.Column('object_id', meta.Integer,
                meta.ForeignKey('core_acl_objects.object_id')),
    meta.Column('post_count', meta.Integer),
    meta.Column('view_count', meta.Integer),
    meta.Column('author_id', meta.Integer,
                meta.ForeignKey('core_users.user_id')),
    meta.Column('username', meta.Unicode(200)),
    meta.Column('title', meta.Unicode(200)),
    meta.Column('text', meta.Unicode),
    meta.Column('timestamp', meta.DateTime)
)

privileges = meta.Table('core_privileges',
    meta.Column('priv_id', meta.Integer, primary_key=True),
    meta.Column('name', meta.Unicode(100))
)

acl_mapping = meta.Table('core_acl_mapping',
    meta.Column('priv_id', meta.Integer,
                meta.ForeignKey('core_privileges.priv_id')),
    meta.Column('subject_id', meta.Integer,
                meta.ForeignKey('core_acl_subjects.subject_id')),
    meta.Column('object_id', meta.Integer,
                meta.ForeignKey('core_acl_objects.object_id')),
    meta.Column('state', meta.Integer)
)

acl_subjects = meta.Table('core_acl_subjects',
    meta.Column('subject_id', meta.Integer, primary_key=True),
    meta.Column('subject_type', meta.String(10))
)

acl_objects = meta.Table('core_acl_objects',
    meta.Column('object_id', meta.Integer, primary_key=True),
    meta.Column('object_type', meta.String(10))
)

acl_subject_join = meta.polymorphic_union({
    'user':     users,
    'group':    groups
}, 'subject_type')

acl_object_join = meta.polymorphic_union({
    'forum':    forums,
    'post':     posts
}, 'object_type')

class CoreTableObserver(DatabaseObserver):

    def after_table_creation(self, table):
        if table is users:
            e = self.ctx.engine.execute
            e(users.insert(), user_id=ANONYMOUS_USER_ID, username='anonymous')
            e(users.insert(), user_id=DEFAULT_USER_ID, username='default')
