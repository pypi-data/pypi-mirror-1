# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.acl
    ~~~~~~~~~~~~~~~~~~

    Pocoo ACL System.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from pocoo.db import meta
from pocoo.pkg.core.forum import Site, Forum, Thread
from pocoo.pkg.core.user import User, Group
from pocoo.pkg.core.db import users, groups, group_members, privileges, \
     forums, posts, acl_mapping, acl_subjects, acl_objects


class AclManager(object):
    """
    Manager object to manage ALCs.
    """
    STRONG_NO = -1
    WEAK_NO = 0
    WEAK_YES = 1
    STRONG_YES = 2

    def __init__(self, ctx, subject):
        self.ctx = ctx
        self.subject = subject
        if isinstance(subject, User):
            self._type = 'user'
        elif isinstance(subject, Group):
            self._type = 'group'
        else:
            raise ValueError('neither user or group specified')

    def allow(self, privilege, obj, force=False):
        """Allows the subject privilege on obj."""
        return self._set(privilege, obj, 1 + bool(force))

    def default(self, privilege, obj):
        """Sets the state for privilege on obj back to weak yes."""
        return self._set(privilege, obj, 0)

    def deny(self, privilege, obj, force=False):
        """Denies the subject privilege on obj."""
        return self._set(privilege, obj, -1 - bool(force))

    def can_access(self, privilege, obj):
        """Checks if the current subject with the required privilege
        somehow. Either directly or when the subject is a user and
        one of its groups can access it."""
        #XXX: maybe this could be one big query instead of 4
        #XXX: this currently does not work correctly, therefore return True
        return True

        if not isinstance(obj, (Forum, Thread, Site.__class__)):
            raise TypeError('obj must be a forum, thread or site')
        privilege = privilege.upper()
        s = self._get_subject_join().alias('s').c

        def do_check(obj, tendency):
            db = self.ctx.engine
            o = self._get_object_join(obj).alias('o').c

            # self check
            r = db.execute(meta.select([acl_mapping.c.state],
                (acl_mapping.c.priv_id == privileges.c.priv_id) &
                (acl_mapping.c.subject_id == s.subject_id) &
                (acl_mapping.c.object_id == o.object_id) &
                (privileges.c.name == privilege)
            ))
            row = r.fetchone()
            if row is not None:
                if row['state'] in (self.STRONG_NO, self.STRONG_YES):
                    return row['state'] == self.STRONG_YES
                tendency = row['state']

            # if the controlled subject is a user check all groups
            if isinstance(self.subject, User):
                r = db.execute(meta.select([acl_mapping.c.state],
                    (acl_mapping.c.object_id == o.object_id) &
                    (acl_mapping.c.subject_id == groups.c.subject_id) &
                    (groups.c.group_id == group_members.c.group_id) &
                    (group_members.c.user_id == self.subject.user_id)
                ))
                while True:
                    row = r.fetchone()
                    if row is None:
                        break
                    state = row[0]
                    if state in (self.STRONG_YES, self.STRONG_NO):
                        return state == self.STRONG_YES
                    if tendency is None:
                        tendency = state
                    elif tendency == self.WEAK_NO and state == self.WEAK_YES:
                        tendency = self.WEAK_YES

            # check related objects
            if isinstance(obj, Thread):
                return do_check(obj.forum, tendency)
            elif isinstance(obj, Forum):
                return do_check(Site, tendency)
            else:
                return tendency

        return do_check(obj, None) in (self.WEAK_YES, self.STRONG_YES)

    def _set(self, privilege, obj, state):
        """Helper functions for settings privileges."""
        privilege = privilege.upper()
        if self.subject.subject_id is None:
            self._bootstrap()
        if obj.object_id is None:
            self._bootstrap_object(obj)
        # special state "0" which means delete
        if not state:
            p = meta.select([privileges.c.priv_id], privileges.c.name == privilege)
            self.ctx.engine.execute(acl_mapping.delete(
                (acl_mapping.c.priv_id == p.c.priv_id) &
                (acl_mapping.c.subject_id == self.subject.subject_id) &
                (acl_mapping.c.object_id == obj.object_id)
            ))
            return
        # touch privilege and check existing mapping
        priv_id = self._fetch_privilege(privilege)
        r = self.ctx.engine.execute(meta.select([acl_mapping.c.state],
            (acl_mapping.c.priv_id == priv_id) &
            (acl_mapping.c.subject_id == self.subject.subject_id) &
            (acl_mapping.c.object_id == obj.object_id)
        ))
        row = r.fetchone()
        if row is not None:
            # this rule exists already
            if row['state'] == state:
                return
            # goddamn, same rule - different state, delete old first
            self._set(privilege, obj, 0)
        # insert new rule
        self.ctx.engine.execute(acl_mapping.insert(),
            priv_id = priv_id,
            subject_id = self.subject.subject_id,
            object_id = obj.object_id,
            state = state
        )

    def _bootstrap(self):
        """This method is automatically called when subject_id is
        None and an subject_id is required."""
        r = self.ctx.engine.execute(acl_subjects.insert(),
            subject_type = self._type
        )
        self.subject.subject_id = r.last_inserted_ids()[0]
        self.subject.save()

    def _bootstrap_object(self, obj):
        """Like _bootstrap but works for objects."""
        objtype = self._get_object_type(obj)
        r = self.ctx.engine.execute(acl_objects.insert(),
            object_type = objtype
        )
        obj.object_id = r.last_inserted_ids()[0]
        obj.save()

    def _get_object_type(self, obj):
        if isinstance(obj, Forum):
            return 'forum'
        elif isinstance(obj, Thread):
            return 'thread'
        elif obj is Site:
            return 'site'
        raise TypeError('obj isn\'t a forum or thread')

    def _get_object_join(self, obj):
        """Returns a subjoin for the object id."""
        t = self._get_object_type(obj)
        if t == 'forum':
            return meta.select([forums.c.object_id],
                forums.c.forum_id == obj.forum_id
            )
        elif t == 'thread':
            return meta.select([posts.c.object_id],
                posts.c.post_id == obj.post_id
            )
        else:
            # XXX: it works ^^
            # i really want something like meta.select('0 as group_id')
            class Fake(object):
                def alias(self, n):
                    class _C(object):
                        class c(object):
                            object_id = 0
                    return _C
            return Fake()

    def _get_subject_join(self):
        """Returns a subjoin for the subject id."""
        if self._type == 'user':
            return meta.select([users.c.subject_id],
                users.c.user_id == self.subject.user_id
            )
        return meta.select([groups.c.subject_id],
            groups.c.group_id == self.subject.group_id
        )

    def _fetch_privilege(self, name):
        """Returns the priv_id for the given privilege. If it
        doesn\'t exist by now the system will create a new
        privilege."""
        r = self.ctx.engine.execute(meta.select([privileges.c.priv_id],
            privileges.c.name == name
        ))
        row = r.fetchone()
        if row is not None:
            return row[0]
        r = self.ctx.engine.execute(privileges.insert(),
            name = name
        )
        return r.last_inserted_ids()[0]

    def __repr__(self):
        if self._type == 'user':
            id_ = self.subject.user_id
        else:
            id_ = self.subject.group_id
        if self.subject.subject_id is None:
            return '<%s %s:%d inactive>' % (
                self.__class__.__name__,
                self._type,
                id_
            )
        return '<%s %s:%d active as %d>' % (
            self.__class__.__name__,
            self._type,
            id_,
            self.subject.subject_id
        )
