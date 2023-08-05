# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.auth
    ~~~~~~~~~~~~~~~~~~~

    Default authentication module.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from datetime import datetime
from pocoo.context import Component
from pocoo.utils.net import IP
from pocoo.application import RequestWrapper
from pocoo.settings import cfg
from pocoo.pkg.core.db import ANONYMOUS_USER_ID
from pocoo.pkg.core.user import User, UserNotFound, check_login_data


class AuthProvider(Component):

    @property
    def auth_name(self):
        """
        has to return the name of the auth module for the configuration
        file. This name defaults to the classname.
        """
        return self.__class__.__name__

    def get_user(self, req):
        """
        This method should either return a valid `User object`_ or ``None``.

        .. _User object: pocoo.pkg.core.user
        """

    def get_user_id(self, session_dict):
        """
        This method should either return the user_id of the user or ``None``.
        """

    def do_login(self, req, username, password):
        """
        This method should update the user session so that the auth provider
        can recognize the user in the ``get_user`` method.
        It has to return a valid ``HttpResponse``, for redirecting to external
        login scripts or ``False``, to display an error message (login failed).
        If it returns ``True`` pocoo will redirect to the last visited page.
        """

    def do_logout(self, req):
        """
        This method should return a valid ``Response`` for redirecting
        to external scripts or ``None``.
        """


class SessionAuth(AuthProvider):

    def get_user(self, req):
        try:
            user_id = req.session['user_id']
            return User(self.ctx, user_id)
        except (KeyError, UserNotFound):
            return None

    def do_login(self, req, username, password):
        user_id = check_login_data(req.ctx, username, password)
        if user_id is not None:
            req.session['user_id'] = user_id
            return True
        return False

    def do_logout(self, req):
        if 'user_id' in req.session:
            req.session.pop('user_id')

    def get_user_id(self, session_dict):
        return session_dict.get('user_id')


class AuthWrapper(RequestWrapper):

    def get_priority(self):
        # after SessionWrapper
        return 3

    def process_request(self, req):
        # XXX: what to do with uid?
        uid = req.session.get('user_id', -1)
        req.auth = AuthController(req)
        req.user = req.auth.get_user()

    def process_response(self, req, resp):
        return resp


def get_auth_provider_mapping(ctx):
    """Returns a list of auth providers."""
    providers = {}
    for comp in ctx.get_components(AuthProvider):
        providers[comp.auth_name] = comp
    return providers


def get_auth_provider(ctx):
    """Returns the enabled auth provider."""
    if 'auth/provider' not in ctx._cache:
        providers = get_auth_provider_mapping(ctx)
        provider = providers[ctx.cfg.get('general', 'auth_module')]
        ctx._cache['auth/provider'] = provider
    return ctx._cache['auth/provider']


class AuthController(object):
    auth_provider = cfg.str('general', 'auth_module')

    def __init__(self, req):
        self.ctx = req.ctx
        self.req = req
        self.provider = get_auth_provider(req.ctx)

    def get_user(self):
        """
        Returns the user for this request
        """
        user = self.provider.get_user(self.req)
        if user is not None:
            user.ip = IP(self.req.environ['REMOTE_ADDR'])
            return user
        # return anonymous user
        return User(self.ctx, ANONYMOUS_USER_ID)

    def do_login(self, username, password):
        """
        Returns a valid ``Response``, for redirecting to external
        login scripts or ``False``, to display an error message (login failed).
        If it returns ``True`` pocoo should redirect to the last visited page.
        """
        rv = self.provider.do_login(self.req, username, password)
        if rv is not False:
            self.req.user = self.get_user()
            return rv
        return False

    def do_logout(self):
        """
        Loggs the user out. Can eiter return None or a Response for
        external redirects.
        """
        # update last login time
        self.req.user.last_login = datetime.now()
        self.req.user.save()
        self.provider.do_logout(self.req)
        #XXX: maybe a bit slow
        self.req.user = self.get_user()
