import paste.fixture
from unittest import TestCase

from authorize_middleware import authorize_request
import authopenid_middleware
import openidprovider_middleware

from openid.fetchers import HTTPFetcher, HTTPResponse, setDefaultFetcher
import cgi

class SessionStub(dict):

    id = '1'

    def save(self):
        pass

class PostProcess:

    def __init__(self):
        self.processed = False

    def __call__(self, environ, username, user_data):
        self.processed = True

class TestSessionMiddleware:

    def __init__(self, app):
        self.app = app
        self.items = SessionStub()

    def __call__(self, environ, start_response):
        environ['beaker.session'] = self.items
        return self.app(environ, start_response)

class FetcherStub(HTTPFetcher):
    """ Fetcher Stub. """

    def __init__(self, app):
        self.app = app

    def fetch(self, url, body=None, headers=None):
        fetch_url = url[len('http://server'):]
        if body is not None:
            parsed = cgi.parse_qsl(body, keep_blank_values=True,
                               strict_parsing=False)
        else:
            parsed = {}

        response = self.app.get(fetch_url, params=parsed, headers=headers)

        resp = HTTPResponse()
        resp.body = response.body
        resp.final_url = url
        resp.headers = response.header_dict
        resp.status = int(response.status)

        return resp


class TestApp:

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        if environ['PATH_INFO']=='/private':
            authorize_request(environ)

        start_response('200 OK', [('Content-type', 'text/plain; charset=UTF-8')])
        return [str('REMOTE_USER' in environ)]

class TestAuthOpenIdMiddleware(TestCase):

    def test_authopenid_basic(self):
        app = TestApp()
        app = authopenid_middleware.middleware(app, loginurl='/login')
        tsm = TestSessionMiddleware(app)
        app = paste.fixture.TestApp(tsm)

        response = app.get('/')
        assert response.status == 200
        response = app.get('/private')
        assert response.status == 301
        assert response.header_dict['location'] == '/login'


class TestOpenIdProviderMiddleware(TestCase):

    def test_whole_process(self):
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return True
        app2 = openidprovider_middleware.middleware(app2, baseurl='http://server/', isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/')
        assert response.body == 'False'

        response = app1.get('/verify')
        assert response.status == 301
        assert response.header_dict['location'] == '/login'
        assert 'error' in tsm1.items
        tsm1.items.clear()

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        assert response.status == 301
        assert 'Location' in response.header_dict
        assert 'error' not in tsm1.items

        response = app2.get(response.header_dict['Location'][len('http://server'):])

        assert response.header_dict['Location'].startswith('http://client')
        response = app1.get(response.header_dict['Location'][len('http://client'):])

        assert response.status == 301
        assert 'REMOTE_USER_OPENID' in tsm1.items
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.header_dict['Location'] == 'http://client/'

        response = app1.get('/')
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.body == 'True'

    def test_decide_page(self):
        """ Test if redirection to decide page happens when necessary."""
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return False
        app2 = openidprovider_middleware.middleware(app2,
                baseurl='http://server/',
                decideurl='/decide',
                isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        response = app2.get(response.header_dict['Location'][len('http://server'):])
        assert response.status == 301
        assert response.header_dict['location'] == '/decide'

    def test_failure_no_decide(self):
        """ Test if authentication fails when no decide page is available."""
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return False
        app2 = openidprovider_middleware.middleware(app2, baseurl='http://server/', isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        response = app2.get(response.header_dict['Location'][len('http://server'):])
        response = app1.get(response.header_dict['Location'][len('http://client'):])
        assert response.status == 301
        assert 'error' in tsm1.items
        assert response.header_dict['location'] == '/login'

    def test_allow(self):
        """ Test if allow works as intended."""
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return False
        def is_allowed(environ, identity, trust_root, params):
            allow = identity == 'http://server/id/test' and trust_root == 'http://client' and \
                    params['test'] == 'test_value'
            return allow
        app2 = openidprovider_middleware.middleware(app2,
                baseurl='http://server/',
                decideurl='/decide',
                isallowed=is_allowed,
                isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        response = app2.get(response.header_dict['Location'][len('http://server'):])
        assert response.status == 301
        assert response.header_dict['location'] == '/decide'
        response = app2.get('/allow', params = {'test': 'test_value'})
        response = app1.get(response.header_dict['Location'][len('http://client'):])
        assert response.status == 301
        assert 'REMOTE_USER_OPENID' in tsm1.items
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.header_dict['Location'] == 'http://client/'

    def test_disallow(self):
        """ Test disallow."""
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return False
        def is_allowed(environ, identity, trust_root, params):
            return False
        app2 = openidprovider_middleware.middleware(app2,
                baseurl='http://server/',
                decideurl='/decide',
                isallowed=is_allowed,
                isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        response = app2.get(response.header_dict['Location'][len('http://server'):])
        assert response.status == 301
        assert response.header_dict['location'] == '/decide'
        response = app2.get('/allow', params = {'test': 'test_value'})
        response = app1.get(response.header_dict['Location'][len('http://client'):])
        assert response.status == 301
        assert 'error' in tsm1.items

    def test_whole_process_with_sqlite(self):
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login',
                database='sqlite:///:memory:')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return True
        app2 = openidprovider_middleware.middleware(app2, baseurl='http://server/', isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/')
        assert response.body == 'False'

        response = app1.get('/verify')
        assert response.status == 301
        assert response.header_dict['location'] == '/login'
        assert 'error' in tsm1.items
        tsm1.items.clear()

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        assert response.status == 301
        assert 'Location' in response.header_dict
        assert 'error' not in tsm1.items

        response = app2.get(response.header_dict['Location'][len('http://server'):])

        assert response.header_dict['Location'].startswith('http://client')
        response = app1.get(response.header_dict['Location'][len('http://client'):])

        assert response.status == 301
        assert 'REMOTE_USER_OPENID' in tsm1.items
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.header_dict['Location'] == 'http://client/'

        response = app1.get('/')
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.body == 'True'

    def test_post_process_action(self):
        """ Test if post-process action is called after login. """

        postprocess = PostProcess()

        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login',
                postprocess=postprocess)
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return True
        app2 = openidprovider_middleware.middleware(app2, baseurl='http://server/', isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test'})
        assert response.status == 301
        assert 'Location' in response.header_dict
        assert 'error' not in tsm1.items

        response = app2.get(response.header_dict['Location'][len('http://server'):])

        assert response.header_dict['Location'].startswith('http://client')
        assert postprocess.processed == False
        response = app1.get(response.header_dict['Location'][len('http://client'):])

        assert response.status == 301
        assert 'REMOTE_USER_OPENID' in tsm1.items
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.header_dict['Location'] == 'http://client/'
        assert postprocess.processed == True

    def test_sreg_utf8(self):
        """Test if SReg response encoded with UTF-8 is handled properly."""
        app1 = TestApp()
        app1_conf = {'authopenid.sreg.required': 'nickname'}
        app1 = authopenid_middleware.middleware(app1, app_conf=app1_conf,
                                                baseurl='http://client',
                                                loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()

        is_authorized = lambda environ, identity, trust_root: True

        nickname = u'\u4e16\u754c'
        get_sreg_data = lambda: {'nickname': nickname}

        app2_conf = {'openidprovider.getsregdata': get_sreg_data}
        app2 = openidprovider_middleware.middleware(app2, app_conf=app2_conf,
                                                    baseurl='http://server/',
                                                    isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/')
        assert response.body == 'False'

        response = app1.get('/verify')
        assert response.status == 301
        assert response.header_dict['location'] == '/login'
        assert 'error' in tsm1.items
        tsm1.items.clear()

        response = app1.get('/verify', params = {'openid':
                                                 'http://server/id/test'})
        assert response.status == 301
        assert 'Location' in response.header_dict
        assert 'error' not in tsm1.items

        response = app2.get(
            response.header_dict['Location'][len('http://server'):]
        )

        assert response.header_dict['Location'].startswith('http://client')
        response = app1.get(
            response.header_dict['Location'][len('http://client'):]
        )

        assert response.status == 301
        assert 'REMOTE_USER_OPENID' in tsm1.items
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert response.header_dict['Location'] == 'http://client/'

        response = app1.get('/')
        assert tsm1.items['REMOTE_USER_OPENID'] == 'http://server/id/test'
        assert tsm1.items['x-wsgiorg.user_data']['nickname'] == nickname
        assert response.body == 'True'










    def test_cookies(self):
        app1 = TestApp()
        app1 = authopenid_middleware.middleware(app1, baseurl='http://client', loginurl='/login')
        tsm1 = TestSessionMiddleware(app1)
        app1 = paste.fixture.TestApp(tsm1)

        app2 = TestApp()
        def is_authorized(environ, identity, trust_root):
            return True
        app2 = openidprovider_middleware.middleware(app2, baseurl='http://server/', isauthorized=is_authorized)
        tsm2 = TestSessionMiddleware(app2)
        app2 = paste.fixture.TestApp(tsm2)
        setDefaultFetcher(FetcherStub(app2))

        response = app1.get('/verify', params = {'openid': 'http://server/id/test', 'rememberme': '1'})
        assert 'set-cookie' in response.header_dict
        cookie_dict = {}
        for item in response.header_dict['set-cookie'].split(';'):
            key, value = item.split('=', 1)
            cookie_dict[key.strip()] = value
        assert 'authopenidcookie' in cookie_dict
        assert 'expires' in cookie_dict
        assert 'Path' in cookie_dict

        response = app2.get(response.header_dict['Location'][len('http://server'):])
        response = app1.get(response.header_dict['Location'][len('http://client'):])
        response = app1.get('/')
        assert 'REMOTE_USER_OPENID' in tsm1.items

        response = app1.get('/',
                extra_environ = {'HTTP_COOKIE': 'authopenidcookie=' + cookie_dict['authopenidcookie']})
        assert response.body == 'True'
        app1.reset()
        response = app1.get('/',
                extra_environ = {'HTTP_COOKIE': 'authopenidcookie=' + cookie_dict['authopenidcookie'] + '1'})
        assert response.body == 'False'
        response = app1.get('/')
        assert response.body == 'False'
