# -*- coding: utf-8 -*-
"""
    pocoo.db
    ~~~~~~~~

    Database support, a thin layer on top of SQLAlchemy.


    How to use the database layer
    =============================

    TODO: this needs to be written.


    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
import sys
import new
import cPickle as pickle
from copy import copy
from itertools import izip

import sqlalchemy

from pocoo import Component
from pocoo.exceptions import PocooRuntimeError


metadata = sqlalchemy.MetaData()


class DatabaseObserver(Component):
    """
    Notifies of database changes.
    """

    def before_table_creation(self, table):
        """
        This is called just before a pending table creation. If this method
        returns False the context will skip the creation of the table.
        """
        return True

    def after_table_creation(self, table):
        """
        This method is called after the creation of a database table.
        """


def get_database_modules(only_names=False):
    """
    Returns a dict of supported database modules.
    """
    def wrapper():
        """yield tuples of available DB engines"""
        try:
            import pysqlite2
            yield 'sqlite', pysqlite2
        except ImportError:
            pass
        try:
            import MySQLdb
            yield 'mysql', MySQLdb
        except ImportError:
            pass
        try:
            try:
                import psycopg as postgres
            except ImportError:
                import psycopg2 as postgres
            yield 'postgres', postgres
        except ImportError:
            pass
    if only_names:
        return [name for name, _ in wrapper()]
    return dict(wrapper())


def get_engine(cfg):
    """
    Returns a new SQLAlchemy engine.
    """
    uri = str(cfg.get('database', 'uri', 'sqlite://'))
    debug = cfg.get_bool('development', 'debug', False)
    debug = debug and cfg.get_bool('database', 'verbose', False)
    return sqlalchemy.create_engine(uri, echo=debug, encoding='utf-8')


def get_metadata(engine):
    """
    Returns a new SQLAlchemy metadata object.
    """
    return sqlalchemy.BoundMetaData(engine)


class Table(sqlalchemy.Table):
    """
    Small wrapper around ``sqlalchemy.Table`` to always
    use the same metadata object.
    """

    class __metaclass__(type(sqlalchemy.Table)):

        def __call__(self, name, *args, **kw):
            return type(sqlalchemy.Table).__call__(self, name, metadata,
                                                   *args, **kw)

    def __repr__(self):
        # pylint: disable-msg=E1101
        return '<%s %r: %s>' % (
            self.__class__.__name__,
            self.name,
            ', '.join(c.name for c in self.c)
        )


class DatabaseModel(object):
    """
    Represents a database object.

    Usage::

        super(User, self).__init__(ctx, users, 'user_id')
    """

    def __init__(self, ctx, table, primary_key, select_q=None):
        self.__engine = ctx.engine
        self.__table = table
        self.__key = primary_key
        self.__select_q = select_q
        self.__orig = None
        self.__cur = {}
        self.__exists = None

    def __get_query(self):
        q = getattr(self.__table.c, self.__key) == \
            getattr(self, self.__key)
        if self.__select_q is not None:
            q &= self.__select_q
        return q

    def __load(self, con=None):
        if con is None:
            con = self.__engine
        q = self.__get_query()
        result = self.__engine.execute(self.__table.select(q))
        row = result.fetchone()
        if row is None:
            self.__exists = False
            return
        self.__orig = {}
        for key, value in izip(result.keys, row):
            if isinstance(value, buffer):
                value = str(value)
            self.__orig[key] = copy(value)
            if key not in self.__cur:
                self.__cur[key] = value
        self.__exists = True

    @property
    def exists(self):
        if self.__exists is None:
            self.__load()
        return self.__exists

    def save(self, con=None):
        """Save changes back to the database. If an connection
        object is given as second argument it's used instead
        of the engine."""
        if not self.exists:
            raise RuntimeError('The object does not exist')
        if con is None:
            con = self.__engine
        if self.__orig is None:
            self.__load(con)
        changed = {}
        for key, value in self.__orig.iteritems():
            try:
                new_value = self.__cur[key]
            except KeyError:
                continue
            if value != new_value:
                changed[key] = new_value
        if not changed:
            return
        q = getattr(self.__table.c, self.__key) == self.__orig[self.__key]
        con.execute(self.__table.update(q), **changed)

    def delete(self, con=None):
        """Delete the object."""
        if not self.exists:
            raise RuntimeError('The object does not exist')
        if con is None:
            con = self.__engine
        q = getattr(self.__table.c, self.__key) == self.__orig[self.__key]
        con.execute(self.__table.delete(q))
        self.__exists = False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('Cannot compare model with %r' %
                            other.__class__.__name__)
        return self.__orig[self.__key] == \
               other._DatabaseModel__orig[self.__key]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %d>' % (
            self.__class__.__name__,
            self.__orig[self.__key]
        )


def lazy_column(column):
    """
    Create a property for a lazy column.
    """
    def fget(self):
        cur = self._DatabaseModel__cur
        if column not in cur:
            self._DatabaseModel__load()
        return cur.get(column)
    def fset(self, value):
        self._DatabaseModel__cur[column] = value
    return property(fget, fset)


def get_column_value(model, column, con=None):
    """
    Return the current column value of a model. That also
    works if there is no lazy column. (For private values
    for example). If con is given it's used instead of the
    default engine.
    """
    if column not in model._DatabaseModel__cur:
        model._DatabaseModel__load(con)
    return model._DatabaseModel__cur.get(column)


def set_column_value(model, column, value):
    """
    Set the current column value.
    """
    model._DatabaseModel__cur[column] = value


def get_initial_column_value(model, column, con=None):
    """
    Return the initial column value. If `con` is given and
    a valid connection object it's passed to the load method
    of the database model, otherwise the default engine is
    used.
    """
    if model._DatabaseModel__orig is None:
        model._DatabaseModel__load(con)
    return model._DatabaseModel__orig[column]


class Pickled(sqlalchemy.TypeDecorator):
    """
    A custom SQLAlchemy column type that stores pickles.
    """
    impl = sqlalchemy.Binary

    def __init__(self, defaultfactory):
        self.defaultfactory = defaultfactory
        super(Pickled, self).__init__()

    def convert_result_value(self, value, dialect):
        if value is None:
            return self.defaultfactory()
        buf = self.impl.convert_result_value(value, dialect)
        # buf is now a read-write buffer, but pickle wants a string
        try:
            return pickle.loads(str(buf))
        except Exception:
            return self.defaultfactory()

    def convert_bind_param(self, value, dialect):
        if value is None:
            return None
        return self.impl.convert_bind_param(pickle.dumps(value, 2), dialect)


class ExternalBlob(object):
    """
    Associates a string column with an external file. Unfortunately
    this can't be a SQLAlchemy column type: it needs access to the
    current context.

    Caution: Remember to call "del object.blob" before deleting a record,
             otherwise the blob file will sit around forever!
    """

    def __init__(self, id_):
        self.id = id_

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        myid = getattr(obj, obj.table.primary_key[0].name)
        if myid is None:
            raise PocooRuntimeError('Object must be committed before manipulating blobs')
        fn = "%s-%s" % (self.id, myid)
        path = os.path.join(obj.ctx.cfg.root, 'blobs', obj.table_name, fn)
        try:
            f = file(path, "rb")
            ret = f.read()
            f.close()
            return ret
        except (IOError, OSError):
            return ""

    def __set__(self, obj, value):
        path = os.path.join(obj.ctx.cfg.root, 'blobs', obj.table_name)
        try:
            os.mkdir(path)
        except OSError:
            pass
        myid = getattr(obj, obj.table.primary_key[0].name)
        if myid is None:
            raise PocooRuntimeError('Object must be committed before manipulating blobs')
        fn = "%s-%s" % (self.id, myid)
        path = os.path.join(path, fn)
        try:
            f = file(path, "wb")
            f.write(value)
            f.close()
        except (IOError, OSError):
            raise PocooRuntimeError('Could not write blob')

    def __delete__(self, obj):
        myid = getattr(obj, obj.table.primary_key[0].name)
        if myid is None:
            raise PocooRuntimeError('Object must be committed before manipulating blobs')
        fn = "%s-%s" % (self.id, myid)
        path = os.path.join(obj.ctx.cfg.root, 'blobs', obj.table_name, fn)
        try:
            os.unlink(path)
        except OSError:
            if os.path.isfile(path):
                raise PocooRuntimeError('Could not delete blob')


meta = new.module('meta')
meta.__dict__.update(sqlalchemy.__dict__)
del meta.__file__
meta.__name__ = 'meta'
meta.Pickled = Pickled
meta.ExternalBlob = ExternalBlob
meta.Table = Table
meta.metadata = metadata
sys.modules['pocoo.db.meta'] = meta
