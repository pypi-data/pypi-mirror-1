# -*- coding: utf-8 -*-
"""
    pocoo.wrappers
    ~~~~~~~~~~~~~~

    Pocoo execution wrappers for various server <-> Python
    communication methods.


    Connecting Pocoo with the web server
    ====================================

    Since web servers don't speak WSGI natively, they must communicate
    with Python using one of several methods.


    CGI
    ---

    CGI is the oldest and slowest method.  For each request, a new Python
    process is started, which means that all modules must be imported and
    all initialization must be done each time.

    If you really need to use CGI, create a simple script like this::

        #!/usr/bin/python
        import sys
        sys.path.append("/path/to/pocoo/package")
        # perhaps add more sys.path directories

        from pocoo.wrappers.cgi import run_cgi
        run_cgi("/path/to/instance/root")

    and make sure it is invoked by your web server (usually by placing
    it into a ``cgi-bin`` directory and making it executable).

    Be sure to adapt the config setting ``general.serverpath``
    accordingly: if the script is accessible as
    ``http://server:port/dir/pocoo.cgi``, set the ``serverpath``
    to ``http://server:port/dir/pocoo.cgi/``.


    mod_python
    ----------

    The advantage of mod_python over CGI is that all initialization happens
    just once and pocoo will handle more requests in less time.

    If you have mod_python and FastCGI on your server, FastCGI will be
    the better alternative since you can run your pocoo instance as a
    different user which can improve security.

    If your web server supports mod_python you have two possibilities to
    let mod_python know where it should serve your pocoo instance.

    If you have access to the apache config you can setup a vhost::

        <VirtualHost *>
            ServerName forum.example.com
            <Location />
                SetHandler mod_python
                PythonAutoReload Off
                PythonPath "['/path/to/pocoo'] + sys.path"
                PythonHandler pocoo.wrappers.modpy::handler
                PythonOption instancepath /path/to/pocoo/instance
            </Location>
        </VirtualHost>

    Sometimes ``mod_python`` doesn't work, then you should try
    ``python-program``.

    If you don't want a vhost but have access to the apache.conf, just
    change the ``Location`` value to your settings.

    If you can only create a ``.htaccess`` file, create a new folder
    somewhere under your document root and add a ``.htaccess`` file
    with the following content::

        SetHandler mod_python
        PythonAutoReload Off
        PythonPath "['/path/to/pocoo'] + sys.path"
        PythonHandler pocoo.wrappers.modpy::handler
        PythonOption instancepath /path/to/pocoo/instance

    It's technically possible to create the Pocoo instance folder inside
    this newly created folder but in this case you have to disallow
    remote users to access it by adding the following to your ``.htaccess``::

        <Files myinstance/*>
            Order deny,allow
            Deny from all
        </Files>


    FastCGI
    -------

    If you want to use pocoo over FastCGI you'll need one of those two
    FastCGI gateways:

    - `flup <http://www.saddi.com/software/flup/>`_ or
    - `python-fastcgi <http://cheeseshop.python.org/pypi/python-fastcgi>`_

    If you're using flup you need to create the following file::

        #!/usr/bin/python
        import sys
        sys.path.append('/path/to/pocoo')
        from pocoo.context import ApplicationContext
        from flup.fcgi import WSGIServer

        app = ApplicationContext('/path/to/pocoo/instance')
        if __name__ == '__main__':
            srv = WSGIServer(app)
            srv.run()

    If you want to use the C implementation ``python-fastcgi`` use this file::

        #!/usr/bin/python
        import sys
        sys.path.append('/path/to/pocoo')
        from pocoo.context import ApplicationContext
        from fastcgi import ForkingWSGIServer

        app = ApplicationContext('/path/to/pocoo/instance')
        if __name__ == '__main__':
            srv = ForkingWSGIServer(app)
            srv.serve_forever()

    Save that file as ``pocoo.fcgi`` in a location the web server can access.
    It's possible to save it inside of the instance folder.

    If you are using apache you can run pocoo by putting this into
    your apache.conf::

        <VirtualHost *>
            ServerName forum.example.com

            AddHandler fcgi-script fcgi
            ScriptAlias / /path/to/the/pocoo.fcgi/
        </VirtualHost>

    If you don't want to run it in the document root use this::

        <VirtualHost *>
            ServerName forum.example.com

            AddHandler fcgi-script fcgi
            ScriptAlias /forum /path/to/the/pocoo.fcgi
        </VirtualHost>

    Note the missing trailing slash in this case.

    For lighttpd, put this into your lighttpd.conf::

        fastcgi.server = (".fcgi" => (
            "localhost" => (
                "min-procs" => 1
                "socket"    => "/tmp/fcgi.sock"
            )
        ))

    Note that lighttpd requires that you use a UNIX socket. You have
    to tell flup to use a socket::

        srv = WSGIServer(app, bindAddress = '/tmp/fcgi.sock')
        srv.run()

    For more information about the gateways, have a look at their
    documentation.


    :copyright: 2006 by the Pocoo team.
    :license: GNU GPL, see LICENSE for more details.
"""
