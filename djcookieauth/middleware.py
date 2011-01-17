# -*- coding: utf-8 -*-
# This file is part of dj-cookieauth released under the Apache 2 license. 
# See the NOTICE for more information.

import base64
import hmac
import hashlib
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User, AnonymousUser


class CookieAuthMiddleware(object):

    def __init__(self):
        self.cookie_name = getattr(settings, 'COOKIE_AUTH_NAME', 
                'AuthSession')


    def process_request(self, request):
        try:
            cookie = request.COOKIES[self.cookie_name]
        except KeyError:
            return

        try:
            auth_session = base64.decode(cookie)
            user, timestr, cur_hash = auth_session.split(":")
        except:
            raise ValueError("Malformed AuthSession cookie. Please clear your cookies.")

        try:
            secret = settings.SECRET_KEY
        except KeyError:
            raise ImproperlyConfigured("secret key isn't set")

        try:
            user_obj = User.objects.get(username=user)
        except User.DoesNotExist:
            return

        now = time.time()
        salt = self.get_user_salt(user_obj)
        full_secret = "%s%s" % (secret, salt)

        expected_hash = hmac.new(full_secret, msg="%s:%s" % (user,
            timestr), digestmod=hashlib.sha256).digest()

        timeout = getattr(settings, 'COOKIE_AUTH_TIMEOUT', 600)
        try:
            timestamp = int(timestr, 16)
        except:
            return

        if now < timestamp + timeout:
            if expected_hash == cur_hash:
                timeleft = timestamp + timeout - now
                request.user = user_obj
                request.user.timeleft = timeleft
                return
        
        request.user = AnonymousUser

    def process_response(self, request, response):
        if not request.user.is_authenticated():

            # delete cookie
            if self.cookie_name in request.COOKIES:
                response.delete_cookie(
                        self.cookie_name,
                        path=settings.SESSION_COOKIE_PATH,
                        domain=settings.SESSION_COOKIE_DOMAIN
                )
            return response

        salt = request.get_user_salt(request.user)

        try:
            secret = settings.SECRET_KEY
        except KeyError:
            raise ImproperlyConfigured("secret key isn't set")

        now = time.time()
        full_secret = "%s%s" % (secret, salt)

        new_hash = hmac.new(full_secret, msg="%s:%s" % (request.user,
            now), digestmod=hashlib.sha256).digest()

        key = "%s:%s:%s" % (request.user, now, new_hash)

        response.set_cookie(
                self.cookie_name, 
                base64.encode(key),
                max_age=None,
                expires=None,
                domain=settings.SESSION_COOKIE_DOMAIN,
                path=settings.SESSION_COOKIE_PATH,
                secure=True,
                httponly=True
        )
        return response

    def get_user_salt(self, user):
        if '$' not in user.password:
            return ''
        algo, salt, hsh = user.password.split('$')
        return salt


    
