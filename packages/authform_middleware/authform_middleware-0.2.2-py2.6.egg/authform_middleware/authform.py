# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 Dalius Dobravolskas <dalius@sandbox.lt>
# All rights reserved.
#
# This software is licensed under MIT licence.
#
# Author: Dalius Dobravolskas <dalius@sandbox.lt>

from paste.httpexceptions import HTTPExceptionHandler

import paste.request
from paste.request import construct_url
from paste.util.import_string import eval_import
import Cookie
import md5
import socket
import struct


class AuthFormHandler(object):
    """
    This middleware is triggered when the authenticate middleware catches
    a 401 response. The form is shown to verify user credentials.
    """


    def __init__(self, app, app_conf, authform_conf):
        self.app = app
        self.loginurl = authform_conf.get('loginurl', '/login')
        self.loginurl_func = authform_conf.get('loginurlfunc', None)
        if isinstance(self.loginurl_func, str):
            self.loginurl_func = eval_import(self.loginurl_func)
        self.session_middleware = authform_conf.get('session_middleware', 'beaker.session')

        self.process_url = authform_conf.get('processurl', '/process')
        self.logout_url = authform_conf.get('logouturl', '/logout')

        self.baseurl = authform_conf.get('baseurl', '')

        self.loggedin_url = authform_conf.get('loggedinurl', '/')

        self.is_authenticated = authform_conf.get('isauthenticated', None)
        if isinstance(self.is_authenticated, str):
            self.is_authenticated = eval_import(self.is_authenticated)

        self.rememberme = authform_conf.get('rememberme', True)
        self.rememberme_param = authform_conf.get('rememberme_param', 'rememberme')
        self.cookie_name = authform_conf.get('cookiename', 'authformcookie')
        self.cookie_expires = authform_conf.get('cookieexpires', 3600.0)
        self.ip_mask = authform_conf.get('ipmask', '255.255.255.0')
        self.cookie_secret = authform_conf.get('cookiesecret', 'secret')
        # Use agent string if you are sure that your site uses single agent.
        # E.g. SWFUpload generates different user agent string.
        self.cookie_use_agent = bool(authform_conf.get('cookieuseagent', 'False'))

    def _generate_cookie_value(self, environ):
        address = environ.get('REMOTE_ADDR','0.0.0.0')
        mask = struct.unpack('>L', socket.inet_aton(self.ip_mask))[0]
        address = struct.unpack('>L', socket.inet_aton(address))[0]

        user_string = socket.inet_ntoa(struct.pack('>L', address & mask))
        if self.cookie_use_agent:
            user_string += environ.get('HTTP_USER_AGENT', '')
        user_string += self.cookie_secret
        return md5.md5(user_string).hexdigest()

    def _check_authformcookie(self, environ):
        cookie_value = ''
        cookies = environ.get('HTTP_COOKIE', '')
        idx = cookies.find(self.cookie_name + '=')
        if idx != -1:
            cookie_value = cookies[idx + len(self.cookie_name)+1:]
            cookie_end = cookie_value.find(';')
            if cookie_end != -1:
                cookie_value = cookie_value[:cookie_end]
        return self._generate_cookie_value(environ) == cookie_value

    def __call__(self, environ, start_response):
        status_ = []
        headers_ = []
        exc_info_ = []

        if not environ.has_key(self.session_middleware):
            raise Exception(
                'The session middleware %r is not present. '
                'Have you set up the session middleware?'%(
                    self.session_middleware
                )
            )

        session = environ[self.session_middleware]

        if environ.get('PATH_INFO') == self.process_url:
            response = self.process(environ, start_response)
            session.save()
            return response
        elif environ.get('PATH_INFO') == self.logout_url:
            if session.has_key('REMOTE_USER'):
                session.pop('REMOTE_USER')
            if session.has_key('x-wsgiorg.user_data'):
                session.pop('x-wsgiorg.user_data')
            session.save()

        def fake_start_response(status, headers, exc_info=None):
            status_.append(status)
            headers_.append(headers)
            exc_info_.append(exc_info)

        if self._check_authformcookie(environ) and session.get('REMOTE_USER'):
            environ['AUTH_TYPE'] = 'form'
            environ['REMOTE_USER'] = session['REMOTE_USER']
            environ['x-wsgiorg.user_data'] = session.get('x-wsgiorg.user_data', {})
        elif session.has_key('x-wsgiorg.auth_error'):
            environ['x-wsgiorg.auth_error'] = session.pop('x-wsgiorg.auth_error')
            session.save()

        result = self.app(environ, fake_start_response)
        if status_[0][:3] == '401':
            session['referer'] = construct_url(environ)
            session.save()
            if self.loginurl_func is not None:
                loginurl = self.loginurl_func(environ)
            else:
                loginurl = self.loginurl
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', loginurl)])
            return []
        else:
            start_response(status_[0], headers_[0], exc_info_[0])
            return result

    def process(self, environ, start_response):
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)

        params = dict(paste.request.parse_formvars(environ))

        session = environ[self.session_middleware]
        authenticated, data = self.is_authenticated(environ, params.get('username', None), params.get('password', None))
        if authenticated:
            session['REMOTE_USER'] = params['username']
            if data:
                session['x-wsgiorg.user_data'] = data

            referer = None
            if 'HTTP_REFERER' in environ:
                if self.loginurl_func is not None:
                    loginurl = self.loginurl_func(environ)
                else:
                    loginurl = self.loginurl
                if not environ['HTTP_REFERER'].endswith(self.process_url) and \
                        not environ['HTTP_REFERER'].endswith(loginurl):
                    referer = environ['HTTP_REFERER']

            if referer is not None:
                redirect_url = referer
            elif 'referer' in session:
                redirect_url = session.pop('referer')
            else:
                redirect_url = self.baseurl + self.loggedin_url
            session.save()
            cookie = Cookie.SimpleCookie()
            cookie[self.cookie_name] = self._generate_cookie_value(environ)
            cookie[self.cookie_name]['path'] = '/'
            if not self.rememberme or self.rememberme_param in params:
                cookie[self.cookie_name]['expires'] = Cookie._getdate(self.cookie_expires)

            start_response('301 Redirect', [('Content-type', 'text/html'),
                ('Location', redirect_url),
                ('Set-Cookie', cookie.output()[len('Set-Cookie: '):])])
            return []
        else:
            session['x-wsgiorg.auth_error'] = data

        if self.loginurl_func is not None:
            loginurl = self.loginurl_func(environ)
        else:
            loginurl = self.loginurl
        start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', loginurl)])

        return []


def strip_base(conf, base):
    result = {}
    for key in conf.keys():
        if key.startswith(base):
            result[key[len(base):]] = conf[key]
    return result

def load_config(options, app_conf, prefix):
    merged = strip_base(app_conf, prefix)

    for key, value in options.items():
        if merged.has_key(key):
            warnings.warn(
                'Key %s with value %r set in the config file is being ' + \
                'replaced with value %r set in the application'%(
                    key,
                    auth_conf_options[key],
                    value
                )
            )
        merged[key.replace('_','.')] = value
    return merged

def middleware(app, app_conf=None, prefix='authform.', handle_httpexception=True, **options):
    if handle_httpexception:
        app = HTTPExceptionHandler(app)

    if app_conf is None:
        app_conf = {}
    authform_conf = load_config(options, app_conf, prefix)

    app = AuthFormHandler(app, app_conf, authform_conf)

    return app
