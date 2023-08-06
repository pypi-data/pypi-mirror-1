import paste.fixture
from unittest import TestCase

from authorize_middleware import authorize_request
import authform_middleware

class SessionStub(dict):
    """ Session stub. """

    id = '1'

    def save(self):
        pass


class TestSessionMiddleware:
    """ Session Middleware Stub."""

    def __init__(self, app):
        self.app = app
        self.items = SessionStub()

    def __call__(self, environ, start_response):
        environ['beaker.session'] = self.items
        return self.app(environ, start_response)


class TestApp:
    """ Test application. """

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        if environ['PATH_INFO']=='/private':
            authorize_request(environ)
        elif environ['PATH_INFO']=='/private2':
            authorize_request(environ)

        start_response('200 OK', [('Content-type', 'text/plain; charset=UTF-8')])
        result = {}
        if 'REMOTE_USER' in environ:
            result['REMOTE_USER'] = environ['REMOTE_USER']
        if 'AUTH_TYPE' in environ:
            result['AUTH_TYPE'] = environ['AUTH_TYPE']
        if 'x-wsgiorg.auth_error' in environ:
            result['x-wsgiorg.auth_error'] = environ['x-wsgiorg.auth_error']
        return [str(result)]


class TestAuthFormMiddleware(TestCase):

    def test_basic(self):
        app = TestApp()
        app = authform_middleware.middleware(app, loginurl='/login2')
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/')
        assert response.status == 200
        response = app.get('/private')
        assert response.status == 301
        assert response.header_dict['location'] == '/login2'
        assert 'referer' in tsm.items

    def test_no_referer(self):
        app = TestApp()
        app = authform_middleware.middleware(app)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/login')
        assert 'referer' not in tsm.items

    def test_authenticated(self):
        app = TestApp()
        def is_authenticated(environ, username, password):
            return True, None
        app = authform_middleware.middleware(app, isauthenticated=is_authenticated)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/private')
        assert 'referer' in tsm.items
        response = app.get('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' not in tsm.items
        assert 'REMOTE_USER' in tsm.items
        response = app.get('/')
        assert 'AUTH_TYPE' in response.body
        assert eval(response.body)['AUTH_TYPE'] == 'form'
        assert 'REMOTE_USER' in response.body

    def test_not_authenticated(self):
        app = TestApp()
        def is_authenticated(environ, username, password):
            return False, 'Failed'
        app = authform_middleware.middleware(app, isauthenticated=is_authenticated)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/private')
        assert 'referer' in tsm.items
        response = app.get('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' in tsm.items
        assert 'REMOTE_USER' not in tsm.items
        assert response.status == 301
        assert response.header_dict['location'] == '/login'
        response = app.get('/')
        assert 'x-wsgiorg.auth_error' in response.body
        assert eval(response.body)['x-wsgiorg.auth_error'] == 'Failed'
        response = app.get('/')
        assert 'x-wsgiorg.auth_error' not in response.body

    def test_loginurl_func(self):
        app = TestApp()

        def loginurl_func(environ):
            if environ['beaker.session']['referer'].endswith('/private'):
                return '/login'
            else:
                return '/login2'

        def is_authenticated(environ, username, password):
            return False, 'Failed'

        app = authform_middleware.middleware(app, loginurlfunc=loginurl_func, isauthenticated=is_authenticated)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        # Access private
        response = app.get('/private')
        assert response.status == 301
        assert response.header_dict['location'] == '/login'
        assert 'referer' in tsm.items
        assert tsm.items['referer'].endswith('/private')

        # Fail on login method
        response = app.post('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' in tsm.items
        assert tsm.items['referer'].endswith('/private')
        assert 'REMOTE_USER' not in tsm.items
        assert response.status == 301
        assert response.header_dict['location'] == '/login'

        # Access private2
        response = app.get('/private2')
        assert response.status == 301
        assert response.header_dict['location'] == '/login2'
        assert 'referer' in tsm.items
        assert tsm.items['referer'].endswith('/private2')

        # Fail on login method
        response = app.post('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' in tsm.items
        assert tsm.items['referer'].endswith('/private2')
        assert 'REMOTE_USER' not in tsm.items
        assert response.status == 301
        assert response.header_dict['location'] == '/login2'

    def test_cookies(self):
        app = TestApp()
        def is_authenticated(environ, username, password):
            return True, None
        app = authform_middleware.middleware(app, isauthenticated=is_authenticated)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/process', params = {'username': 'test', 'password': 'test', 'rememberme': '1'})
        assert 'referer' not in tsm.items
        assert 'REMOTE_USER' in tsm.items
        assert 'set-cookie' in response.header_dict
        cookie_dict = {}
        for item in response.header_dict['set-cookie'].split(';'):
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value
        assert 'authformcookie' in cookie_dict
        assert 'expires' in cookie_dict
        assert 'Path' in cookie_dict

        response = app.get('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' not in tsm.items
        assert 'REMOTE_USER' in tsm.items
        assert 'set-cookie' in response.header_dict
        cookie_dict = {}
        for item in response.header_dict['set-cookie'].split(';'):
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value
        assert 'authformcookie' in cookie_dict
        assert 'expires' not in cookie_dict
        assert 'Path' in cookie_dict

        response = app.get('/',
                extra_environ = {'HTTP_COOKIE': 'authformcookie=' + cookie_dict['authformcookie']})
        assert 'REMOTE_USER' in response.body
        app.reset()
        response = app.get('/',
                extra_environ = {'HTTP_COOKIE': 'authformcookie=' + cookie_dict['authformcookie'] + '1'})
        assert 'REMOTE_USER' not in response.body
        response = app.get('/')
        assert 'REMOTE_USER' not in response.body


    def test_cookies_no_rememberme(self):
        app = TestApp()
        def is_authenticated(environ, username, password):
            return True, None
        app = authform_middleware.middleware(app, isauthenticated=is_authenticated, rememberme=False)
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/process', params = {'username': 'test', 'password': 'test'})
        assert 'referer' not in tsm.items
        assert 'REMOTE_USER' in tsm.items
        assert 'set-cookie' in response.header_dict
        cookie_dict = {}
        for item in response.header_dict['set-cookie'].split(';'):
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value
        assert 'authformcookie' in cookie_dict
        assert 'expires' in cookie_dict
        assert 'Path' in cookie_dict
