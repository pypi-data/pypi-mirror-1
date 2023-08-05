# -*- coding: utf-8 -*-
"""
    pocoo.context
    ~~~~~~~~~~~~~

    Pocoo application context class.


    Pocoo application contexts
    ==========================

    An *application context* is a WSGI application wrapper for the
    `pocoo.application.Pocoo` application that makes it possible to
    serve multiple Pocoo instances within one process, and even within
    one thread.

    Aside from not being able to create autoglobal variables for the
    request, the main problem with that approach is that each instance
    can have different packages and plugins.  Therefore Pocoo creates a
    separate package namespace (``pocoo.pkg___<context id>``) for each
    context, into which the packages of each instance are imported.
    The necessary import hook can be found in `pocoo.ihook`.

    The application context also handles database tables and different
    middlewares for each instance.

    (The separate package namespace can be disabled by creating
    the `ApplicationContext` with ``is_cgi=True``.)

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
from os import path
from random import randint
from urlparse import urlparse, urljoin
from posixpath import join as pathjoin

from jinja.lib import stdlib
import pocoo
from pocoo import Component
from pocoo.db import get_engine, meta, DatabaseObserver
from pocoo.ihook import PackageManager, make_bogus_package, \
     setup_importhook
from pocoo.settings import Configuration, load_config, cfg
from pocoo.template import PocooLoader
from pocoo.utils.debug import dtk
from pocoo.utils.logging import Logger
from pocoo.utils.uri import urlencode
from pocoo.exceptions import PocooRuntimeError, \
     PackageImportError, PackageNotFound, InvalidConfigFile

# package file/directory extension
PACKAGE_EXT = '.pkg'
# name of package metadata files
PACKAGE_MANIFEST_FILE = 'package.conf'


class ApplicationContext(object):
    """
    Since there can be multiple Pocoo instances running in the same process,
    this class provides access to database tables and registered components.

    :Ivariables:
      `app` : `pocoo.application.Pocoo` or other WSGI application
        Pocoo WSGI application wrapped with registered middlewares.
      `cfg` : `pocoo.settings.Configuration`
        Configuration for this instance.
      `serverpath` : string
        Full URL path to the instance, e.g. ``http://some.domain.org/boards/pocoo``.
      `servername` : string
        Server name part of ``serverpath``.
      `charset` : string
        Character set.
      `pkgmanager` : `pocoo.ihook.PackageManager`
        Package manager for this instance.
      `packages` : dict
        Package name <-> Package module mapping.
      `packagemeta` : dict
        Package name <-> Package metadata dict mapping.
      `pkg_prefix` : string
        Prefix of this context's package module namespace.
    """
    #: ID <-> ApplicationContext instance mapping.
    _ids = {}

    #: Unique ID for this context. Is always ``0`` if running in CGI mode.
    id = 0
    _init_done = False

    charset = cfg.str('general', 'charset')
    serverpath = cfg.str('general', 'serverpath')

    def __new__(cls, root, is_cgi=False):
        instance = object.__new__(cls, root, is_cgi)
        if is_cgi:
            new_id = 0
        else:
            # XXX: generate a persistent ID?
            while True:
                new_id = '%05i' % randint(0, 99999)
                if new_id not in cls._ids:
                    break
            # this will setup the import hook only once per process
            setup_importhook()
        instance.id = new_id
        cls._ids[new_id] = instance
        return instance

    def __init__(self, root, is_cgi=False):
        self.cfg = Configuration(root)
        self.charset = self.cfg.get('general', 'charset')
        self.engine = get_engine(self.cfg)
        self.packages = {}
        self.packagemeta = {}
        self.tables = {}
        self.middlewares = []
        self.template_loader = PocooLoader(self)

        self.serverpath = self.cfg.get('general', 'serverpath')
        scheme, netloc, self.scriptname = urlparse(self.serverpath)[:3]
        self.servername = scheme + "://" + netloc

        self._cache = {}
        self._components = {}
        self._instances = {}
        self._instancemap = {}
        self._template_lib = stdlib.clone()

        self._regtypes = dict(
            components = self.register_component,
            tables = self.register_table,
            template_tags = self.register_template_tag,
            template_filters = self.register_template_filter,
            middlewares = self.register_middleware
        )

        if is_cgi:
            pkg_prefix = 'pocoo.pkg'
        else:
            pkg_prefix = 'pocoo.pkg___%s' % self.id
        self.pkg_prefix = pkg_prefix

        make_bogus_package(pkg_prefix)
        self.pkgmanager = PackageManager(pkg_prefix, 'pocoo.pkg')
        # allow plain dirs in pocoo/pkg/
        self.pkgmanager.add_path(path.join(path.dirname(__file__), 'pkg'),
                                 (PACKAGE_EXT, ''))
        # allow only packages with extension in instance dir
        self.pkgmanager.add_path(path.join(self.cfg.root, 'packages'),
                                 (PACKAGE_EXT,))

        # setup packages
        dtk.log("context", "setting up package core")
        self.setup_package('core')
        for pkgname in self.cfg.get('general', 'packages', []):
            dtk.log("context", "setting up package %s", pkgname)
            self.setup_package(pkgname)
        # setup site package, if it exists
        try:
            dtk.log("context", "setting up package site")
            self.setup_package('site')
        except PackageNotFound, e:
            dtk.log("context", str(e))

        # initialize the application itself
        self.app = pocoo.application.setup_app(self)

        self._init_done = True

    def __hash__(self):
        return int(self.id)

    def setup_package(self, pkgname):
        """
        Setup a package named ``pkgname``.  This is only possible during context
        initialization.

        Try to import the package and, if successful, read its ``package.conf`` and
        register the components, tables, template tags and filters and middlewares.

        Put the package into ``self.packages``, also put package info into
        ``self.packagemeta``.

        :raise `PackageNotFound`: If the package cannot be found.
        :raise `PackageImportError`: If the package contains invalid metadata,
             the dependencies are not met or there's an ImportError for
             components listed in the ``package.conf``.
        """
        if self._init_done:
            raise PocooRuntimeError('ApplicationContext.setup_package() called after '
                                    'context initialization is complete')
        if pkgname in self.packages:
            return self.packages[pkgname]

        pman = self.pkgmanager
        if not pman.find_module('%s.%s' % (self.pkg_prefix, pkgname)):
            raise PackageNotFound('Package "%s" not found' % pkgname)
        pmeta = {}
        try:
            manifest = pman.importers[pkgname].get_data(PACKAGE_MANIFEST_FILE)
            load_config(manifest.splitlines(), PACKAGE_MANIFEST_FILE,
                        pmeta, initial_state="section")
        except IOError:
            raise PackageNotFound('Package "%s" (at %s) is missing manifest file "%s"' %
                                  (pkgname, pman.pkgs[pkgname], PACKAGE_MANIFEST_FILE))
        except InvalidConfigFile, e:
            raise PackageImportError('Package "%s": manifest file "%s" is invalid: %s' %
                                     (pkgname, PACKAGE_MANIFEST_FILE, str(e)))
        deps = pmeta.get('depends', [])
        # process dependencies
        for dep in deps:
            try:
                name, ver = dep.split('-')
                ver = tuple(ver.split('.'))
            except ValueError:
                name = dep
                ver = ("0",)
            if name not in self.packagemeta:
                try:
                    self.setup_package(name)
                except PackageImportError, e:
                    raise PackageImportError(e.args[0] + ' (dependency needed by '
                        'package "%s"' % pkgname), None, sys.exc_info()[2]
            installed = self.packagemeta[name].get('version', ("0",))
            if ver > installed:
                raise PackageImportError('Package "%s" needs version %s of package '
                                         '"%s", but only version %s is available' %
                                         (pkgname, '.'.join(ver), name,
                                          '.'.join(installed)))
        try:
            pkg = __import__('%s.%s' % (self.pkg_prefix, pkgname), None, None, ['setup'])
        except ImportError, e:
            raise PackageImportError('Package "%s" cannot be imported: %s' %
                                     (pkgname, e)), None, sys.exc_info()[2]

        # These setting names are documented in pocoo.pkg, and must be
        # updated on every change!
        rmeta = {}
        for entry in 'fullname', 'description', 'author', 'revision':
            rmeta[entry] = pmeta.get(entry, '')
        ver = pmeta.get('version', '0')
        if ver == '*':
            ver = pocoo.__version__
        rmeta['version'] = tuple(ver.split('.'))
        rmeta['depends'] = deps

        def import_from_pkg(thing):
            if '.' in thing:
                module, objname = thing.rsplit('.', 1)
                if module == '__init__':
                    module = ''
                else:
                    module = '.'+module
            else:
                module = ''
                objname = thing
            objname = str(objname)
            return getattr(__import__('%s.%s%s' % (self.pkg_prefix, pkgname, module),
                                      None, None, [objname]), objname)

        try:
            for entryname, regfunc in self._regtypes.iteritems():
                for thing in pmeta.get(entryname, []):
                    if thing == '__parent__': continue
                    obj = import_from_pkg(thing)
                    regfunc(obj, pkgname)
        except (AttributeError, ImportError), e:
            raise PackageImportError('Object "%s" listed in manifest of package '
                                     '"%s" not importable: %s'
                                     % (thing, pkgname, e))

        sfuncname = pmeta.get('setupfunc', None)
        if sfuncname:
            func = import_from_pkg(sfuncname)
            func(self, pkgname)

        self.packages[pkgname] = pkg
        self.packagemeta[pkgname] = rmeta
        return pkg

    def register_component(self, component, pkgname):
        """Register the component. Usually called from `setup_package`."""
        component.package = pkgname
        component.comptypes = []
        for comptype in component.__bases__:
            if comptype is Component:
                raise PocooRuntimeError('The base component class %r does not need '
                                        'to be registered directly' %
                                        component.__name__)
            if issubclass(comptype, Component):
                self._components.setdefault(comptype, []).append(component)
                component.comptypes.append(comptype)
            elif hasattr(comptype, "comptype"):
                # TODO: Find a better way to enable component inheritance
                self._components.setdefault(comptype.comptype, []).append(component)
                component.comptypes.append(comptype.comptype)

    def register_table(self, table, pkgname):
        """Register the table. Usually called from `setup_package`."""
        if table in self.tables:
            raise PocooRuntimeError('Table %r already registered' %
                                    table.name)
        self.tables[table.name] = table

    def register_template_tag(self, tag, pkgname):
        """Register the template tag. Usually called from `setup_package`."""
        self._template_lib.register_tag(tag)

    def register_template_filter(self, filter_, pkgname):
        """Register the template filter. Usually called from `setup_package`."""
        fname = getattr(filter_, 'name', filter_.func_name)
        self._template_lib.register_filter(fname, filter_)

    def register_middleware(self, mware, pkgname):
        """Register the middleware. Usually called from `setup_package`."""
        self.middlewares.append(mware)

    def create_logger(self, component):
        """Create a logger for the component."""
        logger = Logger(self, system=component.__class__.__name__)
        return logger

    def get_component(self, compclass):
        """
        Return the instance of a given component class.
        """
        if compclass not in self._instancemap:
            self._instancemap[compclass] = compclass(self)
        return self._instancemap[compclass]

    def get_components(self, comptype):
        """
        Return a list of all registered components of a given
        component type.
        """
        try:
            instlist = self._instances[comptype]
        except KeyError:
            instlist = self._instances[comptype] = []
            for comp in self._components.get(comptype, ()):
                if comp in self._instancemap:
                    instance = self._instancemap[comp]
                else:
                    instance = comp(self)
                    self._instancemap[comp] = instance
                instlist.append(instance)
        return instlist[:]

    def create_tables(self):
        """Create all registered tables."""
        observers = self.get_components(DatabaseObserver)

        def sort_tables():
            sorter = meta.sql_util.TableCollection()
            for table in self.tables.values():
                sorter.add(table)
            return sorter.sort(reverse=True)

        def do_creation(connection):
            engine = connection.engine
            for table in sort_tables():
                if engine.dialect.has_table(connection, table.name):
                    continue
                for observer in observers:
                    rv = observer.before_table_creation(table)
                    if not rv:
                        break
                else:
                    connection.create(table)
                    for observer in observers:
                        observer.after_table_creation(table)

        self.engine.run_callable(do_creation)

    def make_url(self, *link, **query):
        """
        Return an absolute url for ``link``. If there's
        a query, append it.
        """
        # XXX: ascii only, we have to provide a method in the utils
        query = urlencode(query)
        return pathjoin(
            self.scriptname,
            *map(str, link)
        ) + query

    def make_external_url(self, *link, **query):
        """
        Return an external url for ``link``. If there's
        a query, append it.
        """
        query = urlencode(query)
        return urljoin(
            self.serverpath,
            *map(str, link)
        ) + query

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.cfg.root)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
