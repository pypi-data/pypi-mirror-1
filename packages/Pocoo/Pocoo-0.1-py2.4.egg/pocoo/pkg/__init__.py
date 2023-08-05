# -*- coding: utf-8 -*-
"""
    pocoo.pkg
    ~~~~~~~~~

    Pocoo package hierarchy root.


    Pocoo packages
    ==============

    All package code lives in namespaces under `pocoo.pkg`.
    Packages are imported by the `pocoo.ihook` import hooks.
    They can be plain directories or ZIP files, both are handled in
    the same way (see the description there).

    The package directory or ZIP file must be named ``packagename.pkg``.
    All modules within the package will then be imported into
    ``pocoo.pkg.packagename``.


    Package metadata
    ----------------

    A package must contain a ``package.conf`` file at top level. This
    file contains metadata information about the package.  The config
    file uses the same syntax as the global ``pocoo.conf`` (described
    in `pocoo.settings`).

    An example package config file (from the builtin ``highlight``
    package)::

        fullname = "Pocoo source highlighting package"
        description = "Provides syntax highlighting support."
        author = "Pocoo team"
        version = "1.0"
        depends = list:
            core

        components = list:
            base.HighlightingBBCodeTagProvider
            styles.SimpleHighlightingStyle
            lexers.PythonLexer
            lexers.PHPLexer
            lexers.CppLexer

    As you can see, the file consists of a general information section
    (which can be used e.g. for automated package installation tools to
    detect and install new packages), and a ``components`` list.
    This list determines which components are imported and registered
    with the application context.

    Aside from ``fullname`` etc., there can also be other metadata fields:

    * ``depends`` is a list of dependencies, in the format
      ``packagename`` or ``packagename-version``, e.g. ``core-1.2``.

    Aside from ``components``, there can also be other plugin lists:

    * ``tables``: database tables (see `pocoo.db`)
    * ``template_tags``: new tags for HTML templates (see `pocoo.template`)
    * ``template_filters``: new filters for HTML templates
    * ``middlewares``: custom middlewares which wrap the Pocoo
      application (see `pocoo.application` and
      `pocoo.context.ApplicationContext.register_middleware`)


    Loading packages
    ----------------

    To activate and load packages in a Pocoo instance, add the Python
    package name to the "packages" list in the "general" section of
    ``pocoo.conf``, like that::

        packages = list:
            wikiformatter
            xmlrpc

    Packages are automatically found in the ``pkg`` subdirectory and in the
    instance's root directory (where your configuration file is located).

    The ``core`` package, containing all core functionality to run a board,
    is loaded automatically.


    The site package
    ----------------

    When a new Pocoo instance is created, a ``site.pkg`` directory, with
    ``template`` and ``static`` subdirectories, is created in it.
    This "site package" is loaded automatically and does not have to be
    listed in the ``pocoo.conf`` file.

    That way it is made easy for admins to override a template, to add new
    static content or to add single new components (which must still be
    added to the ``site.pkg/package.conf`` file).


    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

#
# Note: this file is only loaded when no Pocoo package
#       manager is installed, e.g. when creating API documentation.
#
