# -*- coding: utf-8 -*-
"""
    pocoo.pkg.core.captcha
    ~~~~~~~~~~~~~~~~~~~~~~

    Captcha URL Handler.

    Displays a random captcha picture (debugging only).

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from pocoo.application import RequestHandler
from pocoo.http import Response


class CaptchaImage(RequestHandler):
    handler_regexes = ['!captcha$']

    def handle_request(self, req):
        from pocoo.utils.captcha import Captcha
        c = Captcha()
        response = Response(c.generate_image())
        response['Content-Type'] = 'image/png'
        return response
