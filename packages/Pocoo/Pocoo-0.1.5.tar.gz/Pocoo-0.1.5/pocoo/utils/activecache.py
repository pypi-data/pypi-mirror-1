# -*- coding: utf-8 -*-
"""
    pocoo.utils.activecache
    ~~~~~~~~~~~~~~~~~~~~~~~

    Provides an special caching system which uses python code objects
    to mix dynamic and static cache parts.

    At the moment it's just used in the ``core`` package to implement
    the bbcode parser and other text formatters.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import datetime
import marshal


class Node(object):
    """
    A basic node that just stores static text.
    """

    def __init__(self, data):
        self.data = unicode(data)

    def render(self, req, comp):
        return self.data

    def __nonzero__(self):
        return bool(self.data)

    def __repr__(self):
        return '%s(%r)' % (
            self.__class__.__name__,
            self.data
        )


class CallbackNode(Node):
    """
    This nodes calls the ``render_callback`` method of the
    component passed to the render method to insert dynamic content.

    Because the data passed to the callback function is defined
    in the constructor and therefore saved as static data in the
    cache data it must be in a special format. For more information
    about the exact data see the docstring of the ``__init__``
    method.

    For performance reasons there is no type check done. So if you
    pass something to the callback node which isn't compilable it
    will just break with an SyntaxError or it might kill a puppy^Wpony.
    """

    def __init__(self, callback, *data):
        """
        :param data:     must be a list, tuple, int, float, str, unicode
                         or Node also nodes or datetime objects are legal.
                         The important thing is that the ``__repr__``
                         method is evalable, and that the object is in the
                         namespace used for evaluation.
        :param callback: a name for the callback so that the formatter
                         can find it on render.
        """
        self.callback = str(callback)
        self.data = data

    def render(self, req, comp):
        return comp.render_callback(req, self.callback, self.data)

    def __nonzero__(self):
        return True

    def __repr__(self):
        return '%s(%r, %s)' % (
            self.__class__.__name__,
            self.callback,
            ', '.join(repr(x) for x in self.data)
        )


class NodeList(Node, list):
    """
    A nodelist can take a number of other nodes in the
    constructor. The ``__repr__`` method of this node tries to
    optimize the generated code. Because this often doesn't work
    on the first optimisation because nested nodes may be more
    optimizable on a next ``__repr__`` the ``generate_cache``
    function calls the ``__repr__`` function until the result
    is unchanged.
    """

    def __init__(self, *nodes):
        list.__init__(self, nodes)

    def render(self, req, comp):
        return u''.join(node.render(req, comp) for node in self)

    def __nonzero__(self):
        for node in self:
            if node:
                return True
        return False

    def __repr__(self):
        newnodes = []
        tmp = []
        for node in self:
            if not node:
                continue
            if type(node) is Node:
                tmp.append(node.data)
            else:
                if tmp:
                    newnodes.append(repr(Node(u''.join(tmp))))
                    tmp[:] = ()
                newnodes.append(repr(node))
        if tmp:
            newnodes.append(repr(Node(u''.join(tmp))))
        if not newnodes:
            return 'Node(u\'\')'
        if len(newnodes) == 1:
            return newnodes[0]
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(newnodes)
        )


def get_cache_namespace():
    """
    Returns the namespace for the cache environment.
    """
    return {
        'datetime':     datetime,
        'Node':         Node,
        'CallbackNode': CallbackNode,
        'NodeList':     NodeList
    }


def optimize_nodes(node):
    """
    Optimizes the nodelist code::

        >>> nodelist = CallbackNode('quote', (
            u'blackbird',
            NodeList(NodeList(Node(u'<strong>'),
                              Node(u'Hello World!'),
                              Node(u'</strong>')),
                     Node(u'<br />\n'),
                     NodeList(Node(u'<a href="http://www.google.com/">'),
                              Node(u'Test'),
                              Node(u'</a>')))))
        >>> optimize(nodelist)
        CallbackNode('quote', (u'blackbird', Node(u'<strong>Hello World!'
        u'</strong><br />\n<a href="http://www.google.com/">Test</a>')))

    """
    namespace = get_cache_namespace()
    source = repr(node)
    while True:
        new_source = repr(eval(source, namespace))
        if source == new_source:
            break
        source = new_source
    return eval(source, namespace)


def generate_cache(node, syntax_parser, optimize=True):
    """
    Generates the code for the node generation.

    Per default optimisation is enabled. You can deactive it
    by setting the ``optimize`` parameter to ``False``.
    """
    assert isinstance(node, Node), 'can only generate code for nodes'
    if optimize:
        source = repr(optimize_nodes(node))
    else:
        source = repr(node)
    code = compile(source, '<cache>', 'eval')
    return marshal.dumps((str(syntax_parser), code))


def load_cache(cache):
    """Loads the cache and returns the cached nodelist."""
    syntax_parser, code = marshal.loads(cache)
    return eval(code, get_cache_namespace()), syntax_parser
