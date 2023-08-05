# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.acl
    ~~~~~~~~~~~~~~~~~~

    Pocoo ACL System. Stores the data binary on the server.

    structure::
        {PERMRIVILEGE: {ID: PERMISSION}}

    `ID`:
        an integer representing the id. If the id is negative
        it's a post id. Because we don't have negative post
        ids you have to make it absolute. If the id is positive
        it's a forum id. If the id is `0` it means it's a side
        wide privilege.

    `PRIVILEGE`:
        the privilege id.

    'PERMISSION`:
        `2`     strict yes
        `1`     weak yes
        `0`     default no
        `-1`    strict no

    This module uses struct! As a result of that data will
    probably get destroyed when changing the computer
    architecture. Because ACL is more important than just
    status information which could be destroyed without
    major problems we should change that to marshal version
    1 in the near future.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import struct
from pocoo.db import meta, get_column_value, set_column_value
from pocoo.pkg.core.db import privileges, forums, posts, users, \
     groups, group_members


#: permission constants
#: ^^^^^^^^^^^^^^^^^^^^
#: deny the access. If it's in one of the acl joins the
#: function will immediately return with `False` (no access)
PERM_DENY = -1

#: the default value which is a weak deny. It's overrideable
#: by all other rules (even `PERM_ALLOW`) and means no access
#: if not overriden any further
PERM_DEFAULT = 0

#: a weak allow. `PERM_DEFAULT` won't override it, but
#: `PERM_ENFORCE` and `PERM_DENY` will. Means object has access
PERM_ALLOW = 1

#: very strong allow. Permission check function will return
#: immediately with a `True` value that means object has access.
PERM_ENFORCE = 2


class Permission(object):
    """Permission perm constants"""
    deny = PERM_DENY
    default = PERM_DEFAULT
    allow = PERM_ALLOW
    enforce = PERM_ENFORCE

    def __init__(self):
        raise TypeError('cannot create %r instances' %
                        self.__class__.__name-_)


def dump_structure(structure):
    """
    Create a binary dump of the given structure dict. How a structure
    looks like is explained in the docstring of this module.
    """
    result = []
    for priv, id_mapping in structure.iteritems():
        for id, perm in id_mapping.iteritems():
            if perm != PERM_DEFAULT:
                result.append(struct.pack('>lll', id, priv, perm))
    return ''.join(result)


def load_structure(structure):
    """
    load a structure into a dict from the given binary data.
    """
    result = {}
    step = struct.calcsize('l') * 3
    try:
        for idx in xrange(0, len(structure), step):
            id, priv, lvl = struct.unpack('>lll', structure[idx:idx + step])
            if priv not in result:
                d = result[priv] = {}
            else:
                d = result[priv]
            d[id] = lvl
    except struct.error:
        raise ValueError('binary ACL structure broken')
    return result


def copy_structure(structure):
    """
    Return a copy of the given structure with removed empty rows
    and default privileges.
    """
    result = {}
    for priv, id_mapping in structure.iteritems():
        d = {}
        for id, perm in id_mapping.iteritems():
            if perm != PERM_DEFAULT:
                d[id] = perm
        if d:
            result[priv] = d
    return result


def get_privilege(ctx, name, lazy=False, con=None):
    """
    Return the id of the given privilege. If the privilege
    does not exist this method will create a new privilege in
    the database for you. If you pass it a connection object
    it's used instead of the context engine.
    If `lazy` is `True` the function won't create a new entry
    on failure but just return `None`.
    """
    if not isinstance(name, basestring):
        raise TypeError('privilege must be string')
    con = con or ctx.engine
    row = con.execute(privileges.select(
        privileges.c.privilege_name == name
    )).fetchone()
    if not row:
        if lazy:
            return
        result = con.execute(privileges.insert(),
            privilege_name=name
        )
        return result.last_inserted_ids()[0]
    return row.privilege_id


class AclManager(object):
    """
    Basic `AclManager`
    """

    def __init__(self, ctx, load_func):
        if type(self) is AclManager:
            raise TypeError('cannot instanciate abstract AclManager class')
        self.ctx = ctx
        self._load_func = load_func
        self._structure = None

    def _load(self):
        data = self._load_func()
        if data is None:
            self._structure = {}
        else:
            self._structure = load_structure(str(data))

    def _lookup(self, id, priv):
        # load structure if not already done. we use caching
        # so that the acl system doesn't automatically query
        # something on class creation.
        if self._structure is None:
            self._load()

        # look up the id in structure
        return (self._structure.get(priv) or {}).get(id) or PERM_DEFAULT

    def _priv_on_site(self, priv):
        return self._lookup(0, priv)

    def _priv_on_forum(self, priv, forum_id, con):
        # try current forum
        rv = self._lookup(forum_id, priv)
        # we got the default value, try recusion
        if rv in (PERM_DEFAULT, PERM_ALLOW):
            row = con.execute(meta.select([forums.c.parent_id],
                forums.c.forum_id == forum_id
            )).fetchone()
            if row and row[0]:
                rv2 = self._priv_on_forum(priv, row[0], con)
            # recusion not possible, try site
            else:
                rv2 = self._priv_on_site(priv)
            # check wether rv or rv2 are what we want
            return (rv == PERM_ALLOW and rv2 == PERM_DEFAULT) and rv or rv2
        return rv

    def _priv_on_post(self, priv, post_id, con):
        # find root post id
        row = con.execute(meta.select([posts.c.root_post_id, posts.c.forum_id],
            posts.c.post_id == post_id
        )).fetchone()
        if row:
            rv = self._lookup(-row[0], priv)
            # no rule for that post, try the forum the post is
            # stored in.
            if rv not in (PERM_DEFAULT, PERM_ALLOW):
                return rv
            rv2 = self._priv_on_forum(priv, row[1], con)
            # check wether rv or rv2 are what we want
            return (rv == PERM_ALLOW and rv2 == PERM_DEFAULT) and rv or rv2
        # test site
        return self._priv_on_site(priv)

    def _set_priv(self, priv, id, perm):
        if self._structure is None:
            self._load()
        self._structure.setdefault(priv, {})[id] = perm

    def can_access_forum(self, privilege, forum_id):
        """Check if the user can access `forum_id` with `privilege`."""
        if not isinstance(forum_id, (int, long)) or forum_id <= 0:
            raise ValueError('positive integer required')
        def do(con):
            priv = get_privilege(self.ctx, privilege, True, con)
            if priv is None:
                return False
            return self._priv_on_forum(priv, forum_id, con) > 0
        return self.ctx.engine.transaction(do)

    def can_access_post(self, privilege, post_id):
        """Check if thse user can access `post_id` with `privilege`."""
        if not isinstance(post_id, (int, long)) or post_id <= 0:
            raise ValueError('positive integer required')
        def do(con):
            priv = get_privilege(self.ctx, privilege, True, con)
            if priv is None:
                return False
            return self._priv_on_post(priv, post_id, con) > 0
        return self.ctx.engine.transaction(do)

    def can_access_site(self, privilege):
        """Check if the user has the global privilege `privilege`."""
        priv = get_privilege(self.ctx, privilege, True)
        if priv is None:
            return False
        return self._priv_on_site(priv) > 0

    def set_forum_privilege(self, privilege, forum_id, perm):
        """Set `privilege` to `forum_id` with `perm`."""
        if not isinstance(forum_id, (int, long)) or forum_id <= 0:
            raise ValueError('positive integer required')
        priv = get_privilege(self.ctx, privilege)
        self._set_priv(priv, forum_id, perm)

    def set_post_privilege(self, privilege, post_id, perm):
        """Set `privilege` to `post_id` with `perm`."""
        if not isinstance(post_id, (int, long)) or post_id <= 0:
            raise ValueError('positive integer required')
        priv = get_privilege(self.ctx, privilege)
        self._set_priv(priv, -post_id, perm)

    def set_site_privilege(self, privilege, perm):
        """Set the global privilege `privilege` to `perm`."""
        priv = get_privilege(self.ctx, privilege)
        self._set_priv(priv, 0, perm)

    def dump(self):
        """Return a binary dump of the current internal structure."""
        if self._structure is None:
            self._load()
        return dump_structure(self._structure)


class GroupAclManager(AclManager):
    """
    Simple manager for groups. It's basically just a subclass of the
    `AclManager` that overrides the default load function.
    """

    def __init__(self, ctx, group_id, load_func=None):
        if load_func is None:
            def load_func():
                row = ctx.engine.execute(meta.select([groups.c.acl_rules],
                    c.group_id == group_id
                )).fetchone()
                if row:
                    return row[0]
        super(GroupAclManager, self).__init__(ctx, load_func)
        self.group_id = group_id


class UserAclManager(AclManager):
    """
    Permission manager for users. It also handles privileges inherited
    from the groups the user is a member of.
    """

    def __init__(self, ctx, user_id, load_func=None):
        if load_func is None:
            def load_func():
                row = ctx.engine.execute(meta.select([users.c.acl_rules],
                    c.user_id == user_id
                )).fetchone()
                if row:
                    return row[0]
        super(UserAclManager, self).__init__(ctx, load_func)
        self.user_id = user_id
        self._self_structure = None

    def _set_priv(self, priv, id, perm):
        super(UserAclManager, self)._set_priv(priv, id, perm)
        self._self_structure.setdefault(priv, {})[id] = perm

    def _load(self):
        super(UserAclManager, self)._load()
        self._self_structure = copy_structure(self._structure)

        # load group acl rules
        result = self.ctx.engine.execute(meta.select([groups.c.acl_rules],
            (group_members.c.user_id == self.user_id) &
            (group_members.c.group_id == groups.c.group_id)
        ))

        # apply rules into structure
        for row in result:
            structure = load_structure(row[0])
            for priv, id_mapping in structure.iteritems():
                d = self._structure.get(priv) or {}
                for id, perm in id_mapping.iteritems():
                    # override with the rules mentioned in the
                    # comments of the privilege constants
                    if perm in (PERM_DENY, PERM_ENFORCE) or \
                       (perm == PERM_ALLOW and
                        d.get(id) not in (PERM_DENY, PERM_ENFORCE)):
                        d[id] = perm
                # just put the dict into the structure if it's not
                # empty.
                if d:
                    self._structure[priv] = d

    def normalize(self):
        """Call this method to copy all permission information of
        all collected groups to the user permission data."""
        self._self_structure.clear()
        self._self_structure.update(copy_structure(self._structure))

    def dump(self):
        """Return a binary dump of the internal structure just
        for the current user. group permissions are left untouched."""
        if self._self_structure is None:
            self._load()
        return dump_structure(self._self_structure)
