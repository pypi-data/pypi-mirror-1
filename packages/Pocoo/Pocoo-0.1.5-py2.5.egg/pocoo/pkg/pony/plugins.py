# -*- coding: utf-8 -*-
"""
    pocoo.pkg.pony.plugins
    ~~~~~~~~~~~~~~~~~~~~~~

    Display information about packages and components.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""
from os.path import abspath
from pocoo import Component
from pocoo.application import RequestHandler
from pocoo.http import Response, TemplateResponse


class PluginPony(RequestHandler):

    handler_regexes = [r'pony/plugins/$']

    def handle_request(self, req):
        pkgname = req.args.pop('pkg', '')
        compname = req.args.pop('comp', '')


        if pkgname and compname:

            return Response(pkgname)

        elif pkgname:
            return Response(compname + "x")

        else:
            # query packages
            packages = []
            for pkgname in sorted(self.ctx.pkgmanager.pkgs):
                pkg = {'name': pkgname, 'loaded': pkgname in self.ctx.packages,
                       'path': abspath(self.ctx.pkgmanager.pkgs[pkgname])}
                if pkg['loaded']:
                    pkg.update(self.ctx.packagemeta[pkgname])
                packages.append(pkg)

            # query plugin types
            plugintypes = []
            for comp_type in Component.__subclasses__():
                plugintypes.append({
                    'name':    comp_type.__name__,
                    'module':  comp_type.__module__.replace(self.ctx.pkg_prefix,
                                                            'pocoo.pkg'),
                    'plugins': [
                        comp.__module__.split('.')[2] + '::' + comp.__class__.__name__
                        for comp in self.ctx.get_components(comp_type)],
                    'doc':     comp_type.__doc__,
                })
            plugintypes.sort(key=lambda x: x['name'].lower())

            # query plugins
            plugins = {}
            for comp_type in Component.__subclasses__():
                for comp in self.ctx.get_components(comp_type):
                    plugins[comp] = {
                        'name':     comp.__class__.__name__,
                        'package':  comp.__module__.split('.')[2],
                        'types':    [c.__name__ for c in comp.__class__.comptypes],
                        'doc':      comp.__class__.__doc__,
                    }
            plugins = plugins.values()
            plugins.sort(key=lambda x: x['name'].lower())

            # query regexes
            regexes = []
            for comp in self.ctx.get_components(RequestHandler):
                for regex in comp.handler_regexes:
                    if not isinstance(regex, basestring):
                        regex, _ = regex
                    regexes.append({
                        'regex':        regex,
                        'component':    comp.__class__.__name__,
                        'package':      comp.__module__.split('.')[2]
                    })
            regexes.sort(key=lambda x: x['regex'].lower())

            return TemplateResponse("plugins.html",
                packages=packages, plugins=plugins, regexes=regexes,
                plugintypes=plugintypes
            )
