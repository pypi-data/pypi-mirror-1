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


class AuthFormHandler(object):
    """
    This middleware is triggered when the authenticate middleware catches
    a 401 response. The form is shown to verify user credentials.
    """


    def __init__(self, app, app_conf, authform_conf):
        self.app = app
        self.loginurl = authform_conf.get('loginurl', '/login')
        self.session_middleware = authform_conf.get('session_middleware', 'beaker.session')

        self.process_url = authform_conf.get('processurl', '/process')
        self.logout_url = authform_conf.get('logouturl', '/logout')

        self.baseurl = authform_conf.get('baseurl', '')

        self.loggedin_url = authform_conf.get('loggedinurl', '/')

        self.is_authenticated = authform_conf.get('isauthenticated', None)
        if isinstance(self.is_authenticated, str):
            self.is_authenticated = eval_import(self.is_authenticated)

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

        if session.get('REMOTE_USER'):
            environ['REMOTE_USER'] = session['REMOTE_USER']
            environ['x-wsgiorg.user_data'] = session.get('x-wsgiorg.user_data', {})

        result = self.app(environ, fake_start_response)
        if status_[0][:3] == '401':
            session['referer'] = construct_url(environ)
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
            return []
        else:
            start_response(status_[0], headers_[0], exc_info_[0])
            return result

    def process(self, environ, start_response):
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)

        params = dict(paste.request.parse_formvars(environ))

        session = environ[self.session_middleware]
        authenticated, data = self.is_authenticated(environ, params['username'], params['password'])
        if authenticated:
            session['REMOTE_USER'] = params['username']
            if data:
                session['x-wsgiorg.user_data'] = data
            if 'referer' in session:
                redirect_url = session.pop('referer')
            else:
                redirect_url = self.baseurl + self.loggedin_url
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', redirect_url)])
            return []

        start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
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
