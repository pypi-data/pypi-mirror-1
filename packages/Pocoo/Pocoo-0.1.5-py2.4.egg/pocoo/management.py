# -*- coding: utf-8 -*-
"""
    pocoo.management
    ~~~~~~~~~~~~~~~~

    Pocoo management script: provides several command-line actions
    for Pocoo instances.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import os, sys, time
import getopt, random
from os.path import isdir, isfile, abspath, join, exists

import pocoo
from pocoo.utils.debug import use_dtk
# pylint: disable-msg=E0611
from pocoo.utils.console import nocolor, darkgreen, \
     red, purple, bold

def _create_ctx(is_cgi):
    from pocoo.context import ApplicationContext
    root = os.environ.get('POCOO_ROOT', '.')
    ctx = ApplicationContext(root, is_cgi=is_cgi)
    return ctx

def _cfg_file_name():
    root = os.environ.get('POCOO_ROOT', '.')
    return os.path.join(root, 'pocoo.conf')


_handlers = {}

def action(name, desc, opts, args):
    """Make the decorated function a management action."""
    def deco(func):
        func.desc = desc
        func.opts = opts
        func.args = args
        func.__doc__ = desc
        _handlers[name] = func
        return func
    return deco


@action('createinstance', 'Create a new Pocoo instance in <path>.', [], ['<path>'])
def createinst(*args, **opts):
    assert len(args) == 1
    path = abspath(args[0])
    assert isdir(path) or not exists(path), 'argument is not a directory or new path'
    assert not isfile(join(path, 'pocoo.conf')), 'instance already exists in path'

    import pocoo.filetemplates as tmpl

    def writefile(content, *pathitems, **flags):
        content = content % {
            'path': path,
            'executable': sys.executable,
        }

        mode = flags.pop('mode', 0)
        p = join(path, *pathitems[:-1])
        if not isdir(p):
            try:
                os.makedirs(p)
            except (IOError, OSError):
                print 'Could not create directory %s' % p
                return
        p = join(p, pathitems[-1])
        try:
            f = open(p, 'w')
            f.write(content)
            f.close()
        except (IOError, OSError):
            print 'Could not create file %s' % p
            return
        if mode:
            try:
                os.chmod(p, mode)
            except Exception:
                pass


    writefile(tmpl.DEFAULT_CONFIG, 'pocoo.conf')
    writefile(tmpl.MANAGEPY, 'manage.py', mode=0755)
    writefile(tmpl.PACKAGESREADME, 'packages', 'README')
    writefile(tmpl.SITEINITPY, 'packages', 'site.pkg', '__init__.py')
    writefile(tmpl.SITEPACKAGECONF, 'packages', 'site.pkg', 'package.conf')
    writefile(tmpl.SITETEMPLATEREADME, 'packages', 'site.pkg', 'templates', 'README')
    writefile(tmpl.SITESTATICREADME, 'packages', 'site.pkg', 'static', 'README')
    writefile(tmpl.BLOBSREADME, 'blobs', 'README')
    writefile(tmpl.CACHEREADME, 'cache', 'README')
    writefile(tmpl.AVATARSREADME, 'avatars', 'README')

    print 'Successfully created a pocoo instance in directory %s.' % path


@action('listpkg', 'List all packages installed in this instance.', [], [])
def listpkg(*args, **opts):
    assert len(args) == len(opts) == 0

    ctx = _create_ctx(True)
    print ">>> Installed packages (packages marked with * are activated in pocoo.conf):"
    pkgman = ctx.pkgmanager
    for pkgname, path in pkgman.pkgs.iteritems():
        act = (pkgname in ctx.packages) and '*' or ' '
        print "    %s %s  at %s" % (act, pkgname, os.path.abspath(path))


@action('listcomp', 'List all components present in <name> or all activated packages.',
        ['by-package', 'by-comptype'], ['<name>'])
def listcomp(*args, **opts):
    assert len(args) <= 1
    assert len(opts) <= 1, "Cannot give --by-package and --by-comptype"
    bytype = '--by-package' not in opts

    ctx = _create_ctx(True)

    complist = []

    def collect_components(pkgname):
        for comptype, comps in ctx._components.iteritems():
            for comp in comps:
                if comp.package == pkgname:
                    complist.append((pkgname, comptype.__name__, comp))

    if not args:
        for pkgname in ctx.packages:
            collect_components(pkgname)
    else:
        ctx.setup_package(args[0])
        collect_components(args[0])

    maxlens = [0, 0, 0]
    def keyfunc(x):
        maxlens[0] = max(maxlens[0], len(x[0]))
        maxlens[1] = max(maxlens[1], len(x[1]))
        maxlens[2] = max(maxlens[2], len(x[2].__module__ + x[2].__name__)-15)
        if bytype:
            return (x[1], x[0], x[2].__module__, x[2].__name__)
        else:
            return (x[0], x[1], x[2].__module__, x[2].__name__)

    complist.sort(key=keyfunc)

    prev = ''
    for pkgname, comptype, comp in complist:
        if bytype:
            if comptype != prev:
                print "\n>>> %s:" % comptype
                prev = comptype
            mod = '.'.join(comp.__module__.split('.')[2:])
            print "    %s.%s" % (mod, comp.__name__)
        else:
            if pkgname != prev:
                print "\n>>> Package %s:" % pkgname
                prev = pkgname
            mod = '.'.join(comp.__module__.split('.')[3:])
            print "    %s.%s%s %s" % \
                  (mod, comp.__name__, " "*(maxlens[2]-len(comp.__name__)-len(mod)),
                   comptype)


@action('runserver', 'Run a development server, optionally without the '
        'reloader component.', ['no-reloader', 'no-debug'], [])
def runserver(*args, **opts):
    assert not args

    if '--no-debug' not in opts:
        use_dtk()

    if not os.environ.get('RUN_MAIN', '') == 'true':
        if sys.platform[:3] == 'win':
            sys.stderr.write('>>> Hit Ctrl+Break to stop the server\n')
        else:
            sys.stderr.write('>>> Hit Ctrl+C to stop the server\n')

    def start():
        cgi_mode = random.randint(0, 1) == 1
        c1 = time.time()

        ctx = _create_ctx(cgi_mode)
        host = ctx.cfg.get('development', 'hostname', '') or 'localhost'
        try:
            port = int(ctx.cfg.get('development', 'port', '8080'))
        except ValueError:
            port = 8080

        c2 = time.time()
        print "Initialized Pocoo in %.4f seconds." % (c2-c1)

        from pocoo.wrappers.standalone import WSGIServer
        srv = WSGIServer(ctx, host, port)
        srv.serve_forever()
    if '--no-reloader' in opts:
        start()
    else:
        from colubrid import reloader
        reloader.main(start, [_cfg_file_name()])


@action('updatedb', 'Updates the database to the current state', [], [])
def updatedb(*args, **opts):
    ctx = _create_ctx(True)
    ctx.create_tables()
    print 'database now up to date'


@action('createforum', 'Creates a new forum', [], ['<name>', '<description>',
        '<parent>'])
def createforum(*args, **opts):
    assert 3 >= len(args) >= 1, 'up to 3 arguments required'
    ctx = _create_ctx(True)
    forums = ctx.tables['core_forums']
    result = ctx.engine.execute(forums.insert(),
        name=args[0],
        description=len(args) == 2 and args[1] or u'',
        thread_count=0,
        post_count=0,
        parent_id=len(args) == 3 and args[2] or None
    )
    print 'Forum %d created' % result.last_inserted_ids()[-1]


@action('config', 'Configure the component <component>.', [], ['<component>'])
def config(*args, **opts):
    assert len(args) == 1


def _mk_pocoo_context():
    from pocoo.wrappers import cli
    from pocoo.utils.collections import AttrDict

    ctx = _create_ctx(True)
    tables = AttrDict(ctx.tables)

    namespace = {
        'pocoo': pocoo,
        'ctx': ctx,
        'db': ctx.engine,
        'tables': tables,
        'lib': lib_metamodule(),
    }
    for name in cli.__all__:
        namespace[name] = getattr(cli, name)

    return namespace


class lib_metamodule(object):
    """Automatically import library modules on attribute access."""
    def __getattr__(self, name):
        return __import__(name)


PREINITIALIZED = '''\
>>> Preinitialized objects:
    lib:        Python library metamodule (use like `lib.md5`)
    pocoo:      the Pocoo root module
    ctx:        the Pocoo application context for this instance
    db:         a precreated Pocoo db session
    models:     a dict with all registered models
    ... and all public functions from pocoo.wrappers.cli.

    '''

BANNER = darkgreen('*** Pocoo v%s interactive console ***\n') + PREINITIALIZED + \
         "Have fun!"

@action('shell', 'Start an interactive shell. Mode can be "classic" or "ipython", '
        'default is autodetect.', [], ['<mode>'])
def startshell(*args, **opts):
    if len(args) == 0:
        mode = 'ipython'
    elif len(args) == 1:
        mode = args[0].lower()
    else:
        assert False
    namespace = _mk_pocoo_context()

    if mode == 'ipython':
        try:
            import IPython
            sh = IPython.Shell.IPShellEmbed(banner=BANNER % pocoo.__version__)
            sh(global_ns=namespace, local_ns={})
            return
        except ImportError:
            pass
    import code
    code.interact(banner=BANNER % pocoo.__version__, local=namespace)


@action('execute', 'Execute a test file in a Pocoo context (use --help-context to '
        'learn what that is)', ['help-context'], ['<filename>'])
def execute(*args, **opts):
    if len(args) == 0 or len(opts) != 0 :
        print """\
Execute a file in a Pocoo context. A Pocoo context has an ApplicationContext
precreated for this instance and the following objects are available as globals:
""" + PREINITIALIZED
        return
    assert len(args) == 1

    namespace = _mk_pocoo_context()
    print ">>> Executing file %s..." % args[0]
    execfile(args[0], namespace)


def main(root='.'):
    """
    Pocoo command line administration entry point.

    Parse the arguments and call the appropriate action.
    """

    os.environ['POCOO_ROOT'] = root

    if sys.platform[:3] == 'win' or not sys.stderr.isatty():
        # ooh, those poor Windows users don't have proper terminal colors
        nocolor()

    if os.environ.get('RUN_MAIN', '') != 'true':
        sys.stderr.write(purple('*** Pocoo v%s command line administration\n') %
                         pocoo.__version__)
    else:
        sys.stderr.write(purple('>>> Running with reloader\n'))

    action = 'help'  # pylint: disable-msg=W0621
    try:
        action = sys.argv[1]
        handler = _handlers[action]
    except (IndexError, KeyError):
        if action != 'help':
            sys.stderr.write(red('!!! Invalid action: %s\n\n' % action))
        sys.stderr.write('>>> Usage: %s <action> <opts> <args>\n\n' % sys.argv[0])
        sys.stderr.write('>>> Actions:\n')
        for name, handler in _handlers.iteritems():
            opts = ' '.join('[--'+opt+']' for opt in handler.opts)
            args = ' '.join(handler.args)
            sys.stderr.write('    %s %s%s%s\n       - %s\n' %
                             (bold(name), opts, ((opts and args) and " " or ""),
                              args, handler.desc))
        return 1

    try:
        opts, args = getopt.getopt(sys.argv[2:], '', handler.opts + ['help'])
        opts = dict(opts)
        assert '--help' not in opts    # will print usage on --help
        return handler(*args, **opts)
    except (getopt.GetoptError, AssertionError), e:
        # GetoptError: invalid options
        # AssertionError: invalid arguments/options combination
        if len(e.args):
            sys.stderr.write(red('!!! Error: %s\n\n' % e.args[0]))
        sys.stderr.write('>>> Usage: %s %s %s%s%s\n' % (sys.argv[0], action,
                          ' '.join('[--%s]' % opt for opt in handler.opts),
                          handler.opts and ' ' or '',
                          ' '.join(handler.args)))
        sys.stderr.write('       %s\n' % handler.desc)
        return 1
    except SystemExit:
        # a system exit is not an error
        raise
    except KeyboardInterrupt:
        print red('!!! Interrupted.')
        raise SystemExit
    except Exception, e:
        import traceback
        sys.stderr.write(red('An error occurred while executing the action:\n'))
        sys.stderr.write(''.join(traceback.format_exception_only(*sys.exc_info()[:2])))
        raise

if __name__ == '__main__':
    sys.exit(main())
