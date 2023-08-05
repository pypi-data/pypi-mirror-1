# -*- coding: utf-8 -*-
"""
    pocoo.ihook
    ~~~~~~~~~~~

    Import hook for Pocoo packages.


    The Pocoo import hook
    =====================

    A *Pocoo package* is a Python package which contains plugins (named
    *components*).  The package format is described in `pocoo.pkg`.

    Packages can be

    * normal directories, which is the case for builtin packages
    * directories whose name ends with ``.pkg`` or
    * ZIP files whose name ends with ``.pkg``.

    All those packages must be located either in the ``pkg`` subdirectory
    of the Pocoo source tree (*builtin* packages) or in each Pocoo
    instance's root directory (*per-instance* packages).

    Actually, there are two import hooks in this file:

    * `PackageManager`: A ``sys.meta_path`` import hook that imports
      Pocoo packages into the ``pocoo.pkg`` namespace.

      This hook is necessary to import Pocoo packages and must therefore
      be installed in any case.

    * `new__import__`: A replacement ``__import__`` function that acts on
      imports of Pocoo package modules from different application contexts
      and dispatches them to the proper context.  To achive that, it analyzes
      the ``globals`` argument which contains the module name of the
      importing module and therefore the context ID.

      This hook is set up by calling `setup_importhook` (which is usually
      done by `pocoo.context.ApplicationContext.__new__`).
      It can be left unused if there is only one Pocoo instance in the
      current process, which is true for CGI and command line requests.


    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import sys
import os
import imp
from os.path import abspath, join, splitext
from zipimport import zipimporter, ZipImportError

from pocoo.exceptions import MissingResource
from pocoo.utils.debug import dtk


class PlainPackageImporter(object):
    """
    Import manager for plain pocoo packages (\*.pkg dirs).
    """

    def __init__(self, filename, virtual):
        self.abspath = abspath(filename)
        self.virtual = virtual
        self._cache = {}

    def __repr__(self):
        return '<PlainPackageImporter for "%s">' % self.abspath

    def find_module(self, impname, path=None):
        if impname == '':
            # this always succeeds (hack needed due to Windows problems)
            self._cache[impname] = (None, self.abspath, ('', '', 5))
            return self

        try:
            self._cache[impname] = imp.find_module(impname, [self.abspath])
        except ImportError:
            return None
        return self

    def load_module(self, impname):
        """Load the module ``impname`` and register it in ``sys.modules``."""
        if impname not in self._cache:
            self._cache[impname] = imp.find_module(impname, [self.abspath])
        virtualname = self.virtual + (impname and '.' + impname)
        return imp.load_module(virtualname, *self._cache[impname])

    def get_source(self, impname):
        if impname not in self._cache:
            return None
        virtualname = self.virtual + (impname and '.' + impname)
        fn = sys.modules[virtualname].__file__
        if fn.endswith('.pyc') or fn.endswith('.pyo'):
            fn = fn[:-1]
        f = file(fn, 'U')
        contents = f.read()
        f.close()
        return contents

    def get_data(self, filename):
        f = file(join(self.abspath, filename), 'rb')
        contents = f.read()
        f.close()
        return contents


class ZipPackageImporter(zipimporter):
    """
    Extension for zipimporter that can import submodules and place
    them in a virtual package in a straightforward manner.
    """

    def __init__(self, filename, virtual):
        zipimporter.__init__(self, filename)
        self.virtual = virtual
        self.abs_archive = abspath(self.archive)

    def find_module(self, impname, path=None):
        """Return self if the module "fullname" is in the ZIP file."""
        impname = impname.replace('.', os.sep)
        if impname == '':
            impname = '__init__'
        try:
            self.is_package(impname)
        except Exception:
            return None
        return self

    def load_module(self, impname):
        """Load the module "impname" and register it in sys.modules."""
        modname = '%s%s%s' % (self.virtual, (impname and "."), impname)
        mod = sys.modules.setdefault(modname, imp.new_module(modname))
        impname = impname.replace('.', '/')
        if impname == '':
            # top-level package -- hack around
            impname = '__init__'
            modname = modname[:-1]
            mod.__path__ = []
        is_pkg = self.is_package(impname)
        code = self.get_code(impname)
        if is_pkg:
            mod.__path__ = []
            mod.__file__ = join(self.abs_archive, impname, '__init__.py')
        else:
            mod.__file__ = join(self.abs_archive, impname + '.py')
        exec code in mod.__dict__
        return mod

    def get_source(self, impname):
        impname = impname.replace('.', '/')
        if impname == '':
            impname = '__init__'
        return zipimporter.get_source(self, impname)


class PackageManager(object):
    """
    Import hook that can import modules from Pocoo packages
    (\*.pkg dirs and ZIP files).

    :ivar prefix: The actual prefix for which this class should
        import modules.
    :ivar virtualprefix: The virtual prefix under which the imported
        modules should be placed in the module namespace.
    """

    def __init__(self, prefix, virtualprefix):
        """
        :Parameters:
          `prefix` : string
            real module name prefix, e.g. "pocoo.pkg___12345"
          `virtualprefix` : string
            virtual module name prefix, e.g. "pocoo.pkg"
        """
        self.prefix = prefix+'.'
        self.prefixlen = len(prefix)+1
        self.virtualprefix = virtualprefix+'.'

        self.paths = []
        self.pkgs = {}
        self.importers = {}
        self._imp_cache = {}
        self._res_cache = {}

        # register as an import hook
        sys.meta_path.append(self)

    def add_path(self, path, pkg_extensions):
        """
        Add a path in which packages are to be found.

        Only files and directories whose file name extension
        is in ``pkg_extensions`` will be added.

        :raise ImportError: if ``path`` cannot be found.
        """
        try:
            files = os.listdir(path)
        except OSError:
            raise ImportError("directory '%s' not found" % path)
        self.paths.append(abspath(path))

        # find all pocoo packages in path
        for fname in files:
            base, ext = splitext(fname)
            if ext in pkg_extensions and \
               base.replace('_', '').isalnum() and base[0].isalpha():
                self.pkgs[base] = join(path, fname)

    def find_module(self, fullname, path=None):
        """
        Find a module: first, see if we know the package, then try to create
        an importer for it. Then, let it find the submodule.

        :return: self if module found, else None.
        """
        if not fullname.startswith(self.prefix):
            return None
        if fullname in self._imp_cache:
            return self

        impname = fullname[self.prefixlen:]
        pkgname = impname.split('.')[0]
        if pkgname not in self.pkgs:
            return
        if pkgname not in self.importers:
            fullpath = self.prefix + pkgname
            try:
                importer = ZipPackageImporter(self.pkgs[pkgname], fullpath)
            except ZipImportError:
                importer = PlainPackageImporter(self.pkgs[pkgname], fullpath)
            self.importers[pkgname] = importer
        else:
            importer = self.importers[pkgname]
        submodule = impname[len(pkgname)+1:]
        if importer.find_module(submodule):
            self._imp_cache[fullname] = (importer, submodule)
            return self
        return None

    def load_module(self, fullname):
        """
        Load the module, using the package from _imp_cache.

        :return: The loaded module.
        :rtype: module
        """
        if (fullname not in self._imp_cache) and not self.find_module(fullname):
            raise ImportError("module '%s' not found" % fullname)

        importer, submodule = self._imp_cache[fullname]
        mod = importer.load_module(submodule)
        mod.__loader__ = self
        dtk.log("ihook", "imported %s as %s", mod.__file__, mod.__name__)
        return mod

    def get_source(self, fullname):
        """Return the source code for a given module."""
        # fullname is in form "pocoo.pkg.xyz"
        fullname = fullname.replace(self.virtualprefix, self.prefix)
        if (fullname not in self._imp_cache) and not self.find_module(fullname):
            raise ImportError("module '%s' not found" % fullname)
        importer, submodule = self._imp_cache[fullname]
        return importer.get_source(submodule)

    def get_resource(self, restype, subtype, name, *priority):
        """
        Return first matching resource data associated with the resource type,
        subtype and name. Packages in priority are searched first.

        :rtype: string
        :raise MissingResource: If the resource cannot be found.
        """
        try:
            importer, path = self._res_cache[restype, subtype, name, priority]
            return importer.get_data(path)
        except KeyError:
            paths = (
                join(restype, subtype, name),
                join(restype, name),
            )
            importers = self.importers.values()
            for pkgname in priority:
                if pkgname in self.importers:
                    # XXX: This duplicates the item(s)
                    importers.insert(0, self.importers[pkgname])
            for path in paths:
                # pylint: disable-msg=W0631
                for importer in importers:
                    try:
                        data = importer.get_data(path)
                        break
                    except IOError:
                        pass
                else:
                    continue  # not found here: continue the outer "for"
                # now that we found data in path, cache it
                self._res_cache[restype, subtype, name, priority] = \
                                         (importer, path)
                return data
            raise MissingResource("resource %s:%s:%s not found (missing "
                                  "extension?)" % (restype, subtype, name))

    def get_resources(self, restype, subtype, name):
        """
        Get all resources associated with restype, subtype and name.

        :rtype: list of strings
        """
        if subtype:
            paths = (join(restype, subtype, name), join(restype, name))
        else:
            paths = (join(restype, name),)
        result = []
        for path in paths:
            for importer in self.importers.values():
                try:
                    result.append(importer.get_data(path))
                except IOError:
                    pass
        return result


def make_bogus_package(name):
    """
    Create a new package named ``name``, put it into ``sys.modules``
    and set it as an attribute of its parent, if the latter exists.

    :return: the new package module.
    :rtype: module
    """
    if name in sys.modules:
        return sys.modules[name]
    mod = imp.new_module(name)
    mod.__file__ = ''
    mod.__path__ = []
    sys.modules.setdefault(name, mod)
    parts = name.split('.')
    if len(parts) == 1:
        return mod

    parent = sys.modules[parts[0]]
    for part in parts[1:-1]:
        parent = getattr(parent, part, None)
        if parent is None:
            # the parent module is not imported yet
            return mod

    setattr(parent, parts[-1], mod)
    return mod


class DispatchingNamespace(object):
    """
    A module surrogate that automatically imports submodules
    on attribute access. Can only be used from Pocoo packages.
    """

    def __init__(self, name):
        self.__dict__['name'] = name

    def __getattr__(self, name):
        callername = sys._getframe(1).f_globals.get('__name__', '')
        if not callername.startswith('pocoo.pkg___'):
            raise AttributeError('cannot access Pocoo package from non-package')
        try:
            return sys.modules[callername[:18] + name]
        except KeyError:
            raise AttributeError('you must first import package %s' % name)

    def __setattr__(self, name, value):
        raise AttributeError('cannot set attributes of ' + self.name)


def new__import__(name, globs=None, locs=None, fromlist=None, *args):
    """
    Replacement __import__ builtin.
    """
    # the *args is for the 2.5 "level" argument
    # old__import__: pylint: disable-msg=E0602
    if not name.startswith('pocoo.pkg.'):
        return old__import__(name, globs, locs, fromlist, *args)
    parentname = globs.get('__name__', '')
    if not parentname.startswith('pocoo.pkg___'):
        raise ImportError('Cannot import Pocoo package from non-package')
    return old__import__(parentname[:17] + name[9:], globs, locs,
                         fromlist, *args)


def setup_importhook():
    """
    Install the new __import__ builtin.
    """
    import __builtin__
    if __builtin__.__import__ is not new__import__:
        if not hasattr(__builtin__, 'old__import__'):
            __builtin__.old__import__ = __builtin__.__import__
        __builtin__.__import__ = new__import__

        import pocoo
        pkg = DispatchingNamespace('pocoo.pkg')
        sys.modules['pocoo.pkg'] = pocoo.pkg = pkg
