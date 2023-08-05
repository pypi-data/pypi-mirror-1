# -*- coding: utf-8 -*-
"""
    pocoo
    ~~~~~

    Welcome to the Pocoo API documentation!


    Important documentation links
    =============================

    =====================================  =====================================
    Application context: `pocoo.context`   Package system: `pocoo.pkg`
    Webserver gateways: `pocoo.wrappers`   Import hook: `pocoo.ihook`
    Form validation: `pocoo.utils.form`    Config format: `pocoo.settings`
    =====================================  =====================================


    The Pocoo component architecture (aka plugin API)
    =================================================

    Pocoo provides a complex package system which allows developers
    to extend the application very easily.


    Context
    -------

    Each component is bound to a specific **application context**,
    representing one Pocoo instance.  To create a context you must
    provide the instance root directory::

        from pocoo.context import ApplicationContext
        ctx = ApplicationContext('path/to/my/instance')

    See `pocoo.context` for details.

    A special import hook makes sure that there can be multiple
    application contexts in one Python process, see `pocoo.ihook`
    for details.


    Components
    ----------

    Apart from little very basic functionality, everything that constitutes
    Pocoo is organized in **components**.  A component is a class that
    inherits from one or more interface classes, called **component types**.

    Each component type serves a certain purpose.  For example, there are
    ``RequestHandlers``, which map URLs to actions, or ``MarkupFormats``,
    which parse the contains of postings and convert them to HTML.
    For each of those component types, you can create additional components
    that inherit from them and provide additional possibilites, e.g. a new
    markup format or a new URL.

    For each component type, code can query all available components and
    iterate over them.  At most one instance of a specific Component class
    is created and reused.

    Defining a component type
    ^^^^^^^^^^^^^^^^^^^^^^^^^

    You define a new component type by creating a class that inherits from
    `Component`. In it, you define all attributes and methods that a
    component must override::

        from pocoo import Component

        class UserGreeter(Component):
            "Gets a greeting for the user."

            #: The level of politeness.
            politeness = 0

            def get_greeting(self):
                "Return a greeting as a string."
                return ""

    This component type can now be used to create real components::

        from pocoo.pkg.mypackage import UserGreeter

        class DefaultGreeter(UserGreeter):
            politeness = 1
            def get_greeting(self, username):
                return "Hello " + username

        class PoliteGreeter(UserGreeter):
            politeness = 2
            def get_greeting(self):
                return "How do you do, %s?" % username

    Component instances always have a ``ctx`` attribute which refers
    to the application context the component instance belongs to.

    You can now query all ``UserGreeter`` components from anywhere of the
    application where you have access to a context object. (This requires
    that the components are registered to the context, so they must be listed
    in the ``package.conf`` file, see `pocoo.pkg`)::

        from pocoo.pkg.mypackage import UserGreeter

        def do_something(ctx):
            [...]
            for comp in ctx.get_components(UserGreeter):
                if comp.politeness == ctx.cfg.get('general', 'politeness'):
                    greeting = comp.get_greeting()
            [...]


    Packages
    --------

    Components are bundled in *packages*.  Every package contains
    a set of components implementing specific functionality.
    Packages are easy to install and to extend.

    For a description of the package format, see `pocoo.pkg`.


    :copyright: 2004-2006 by the Pocoo team.
    :license: GNU GPL, see LICENSE for more details.
"""
# This may not contain "dev", "alpha" or something else
__version__ = '0.1'
__docformat__ = 'reStructuredText'
__license__ = 'GNU General Public License'


# This class is here to avoid circular dependencies
# between pocoo.* modules.

class Component(object):
    """Base Component class."""

    def __init__(self, ctx):
        """Store the context as ``self.ctx``."""
        self.ctx = ctx
