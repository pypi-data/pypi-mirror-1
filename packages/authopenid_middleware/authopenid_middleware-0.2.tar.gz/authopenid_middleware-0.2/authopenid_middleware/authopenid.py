# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 Dalius Dobravolskas <dalius@sandbox.lt>
# All rights reserved.
#
# This software is licensed under MIT licence.
#
# Author: Dalius Dobravolskas <dalius@sandbox.lt>

from openid.store.sqlstore import MySQLStore, PostgreSQLStore, SQLiteStore
from openid.store.memstore import MemoryStore
from openid.consumer import consumer
from openid.extensions import sreg, pape, ax

from paste.httpexceptions import HTTPExceptionHandler

import paste.request
from paste.request import construct_url
from paste.util.import_string import eval_import

from parseurl import parse_url

import Cookie
import struct
import socket
import md5

class AuthOpenIdHandler(object):
    """
    This middleware is triggered when the authenticate middleware catches
    a 401 response. The form is submitted to the verify URL which the other
    middleware handles
    """


    def __init__(self, app, app_conf, authopenid_conf):
        self.app = app
        self.loginurl = authopenid_conf.get('loginurl', '/login')
        self.session_middleware = authopenid_conf.get('session_middleware', 'beaker.session')

        self.verify_url = authopenid_conf.get('verifyurl', '/verify')
        self.process_url = authopenid_conf.get('processurl', '/process')

        self.baseurl = authopenid_conf.get('baseurl', '')

        self.sreg_required = []
        sreg_required = authopenid_conf.get('sreg.required')
        if sreg_required:
            self.sreg_required = [opt.strip() for opt in sreg_required.split(',')]

        self.sreg_optional = []
        sreg_optional = authopenid_conf.get('sreg.optional')
        if sreg_optional:
            self.sreg_optional = [opt.strip() for opt in sreg_optional.split(',')]

        self.sreg_policyurl = authopenid_conf.get('sreg.policyurl', '')

        self.ax_required = []
        ax_required = authopenid_conf.get('ax.required')
        if ax_required:
            self.ax_required = [opt.strip() for opt in ax_required.split(',')]

        self.loggedin_url = authopenid_conf.get('loggedinurl', '/')
        self.logout_url = authopenid_conf.get('logouturl', '/logout')

        self.postprocess = authopenid_conf.get('postprocess', None)
        if isinstance(self.postprocess, str):
            self.postprocess = eval_import(self.postprocess)

        self.rememberme = authopenid_conf.get('rememberme', 'True') == 'True'
        self.rememberme_param = authopenid_conf.get('rememberme_param', 'rememberme')
        self.cookie_name = authopenid_conf.get('cookiename', 'authopenidcookie')
        self.cookie_expires = float(authopenid_conf.get('cookieexpires', 3600.0))
        self.ip_mask = authopenid_conf.get('ipmask', '255.255.255.0')
        self.cookie_secret = authopenid_conf.get('cookiesecret', 'secret')

        self._get_store(authopenid_conf)

    def _get_store(self, app_conf):
        """ Try getting store from configuration. """
        if 'database' in app_conf:

            url = parse_url(app_conf['database'])
            p = {}
            if 'user' in url and url['user']:
                p['user'] = url['user']
            if 'passwd' in url and url['passwd']:
                p['passwd'] = url['passwd']
            if 'host' in url and url['host']:
                p['host'] = url['host']
            if 'port' in url and url['port']:
                p['port'] = url['port']

            if url['drivername'] == 'mysql':
                from mysqlrecycling import MySQLRecyclingConnection
                p['db'] = url['db']
                conn = MySQLRecyclingConnection(**p)
                self.store = MySQLStore(conn)
            elif url['drivername'] == 'sqlite':
                from sqlitedelayed import SQLiteDelayed
                conn = SQLiteDelayed(url['db'], **p)
                self.store = SQLiteStore(conn)
                if url['db'] == ':memory:':
                    self.store.createTables()
        else:
            self.store = MemoryStore()

    def _generate_cookie_value(self, environ):
        address = environ.get('REMOTE_ADDR','0.0.0.0')
        mask = struct.unpack('>L', socket.inet_aton(self.ip_mask))[0]
        address = struct.unpack('>L', socket.inet_aton(address))[0]

        user_string = socket.inet_ntoa(struct.pack('>L', address & mask)) + \
                environ.get('HTTP_USER_AGENT', '') + \
                self.cookie_secret
        return md5.md5(user_string).hexdigest()

    def _check_authopenidcookie(self, environ):
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

        if environ.get('PATH_INFO') == self.verify_url:
            response = self.verify(environ, start_response)
            session.save()
            return response
        elif environ.get('PATH_INFO') == self.process_url:
            response = self.process(environ, start_response)
            session.save()
            return response
        elif environ.get('PATH_INFO') == self.logout_url:
            if session.has_key('REMOTE_USER_OPENID'):
                session.pop('REMOTE_USER_OPENID')
            if session.has_key('x-wsgiorg.user_data'):
                session.pop('x-wsgiorg.user_data')
            session.save()

        def fake_start_response(status, headers, exc_info=None):
            status_.append(status)
            headers_.append(headers)
            exc_info_.append(exc_info)

        if session.get('error'):
            environ['x-wsgiorg.auth_error'] = session.pop('error')
            session.save()

        if self._check_authopenidcookie(environ) and session.get('REMOTE_USER_OPENID'):
            environ['REMOTE_USER'] = session['REMOTE_USER_OPENID']
            environ['x-wsgiorg.user_data'] = session.get('x-wsgiorg.user_data', {})
            environ['AUTH_TYPE'] = 'openid'

        result = self.app(environ, fake_start_response)
        if status_[0][:3] == '401':
            session['referer'] = construct_url(environ)
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
            return []
        else:
            start_response(status_[0], headers_[0], exc_info_[0])
            return result

    def verify(self, environ, start_response):
        session = environ[self.session_middleware]

        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)
        params = dict(paste.request.parse_formvars(environ))
        openid_url = params.get('openid')
        if not openid_url:
            session['error'] = 'No OpenID URL given.'
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
            return []
        oidconsumer = self._get_consumer(environ)
        try:
            request_ = oidconsumer.begin(openid_url)
        except consumer.DiscoveryFailure, exc:
            session['error'] = str(exc[0])
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
            return []
        else:
            if request_ is None:
                session['error'] = 'No OpenID services found for %s' % openid_url
                session.save()
                start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
                return []
            else:
                self._get_referer(environ)
                if self.sreg_required or self.sreg_optional:
                    sreg_request = sreg.SRegRequest(
                        required=self.sreg_required,
                        optional=self.sreg_optional,
                        policy_url=self.sreg_policyurl)
                    request_.addExtension(sreg_request)

                if len(self.ax_required) > 0:
                    ax_request = ax.FetchRequest()
                    for ax_attr in self.ax_required:
                        attr_info = ax.AttrInfo(ax_attr, required=True, alias='email')
                        ax_request.add(attr_info)
                    request_.addExtension(ax_request)

                pape_request = pape.Request([pape.AUTH_PHISHING_RESISTANT])
                request_.addExtension(pape_request)

                trust_root = baseurl
                return_to = baseurl + self.process_url

                cookie = Cookie.SimpleCookie()
                cookie[self.cookie_name] = self._generate_cookie_value(environ)
                cookie[self.cookie_name]['path'] = '/'
                if not self.rememberme or self.rememberme_param in params:
                    cookie[self.cookie_name]['expires'] = Cookie._getdate(self.cookie_expires)

                if request_.shouldSendRedirect():
                    redirect_url = request_.redirectURL(trust_root, return_to)

                    start_response('301 Redirect', [('Content-type', 'text/html'),
                        ('Location', redirect_url),
                        ('Set-Cookie', cookie.output()[len('Set-Cookie: '):])
                        ])
                    return []
                else:
                    # This gets called with sites such as myopenid.com
                    form_html = request_.formMarkup(
                        trust_root, return_to,
                        form_tag_attrs={'id': 'openid_message'})
                    content = """<html><head><title>OpenID transaction in progress</title></head>
                        <body onload='document.getElementById("%s").submit()'>
                        %s
                        </body></html>
                        """ % ('openid_message', form_html)
                    start_response(
                        "200 OK",
                        [
                            ('Content-Type', 'text/html'),
                            ('Content-Length', str(len(content))),
                            ('Set-Cookie', cookie.output()[len('Set-Cookie: '):])
                        ]
                    )
                    return [content]

    def process(self, environ, start_response):
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)

        params = dict(paste.request.parse_querystring(environ))
        oidconsumer = self._get_consumer(environ)
        decoded_params = {}
        for k in params:
            decoded_params[k] = params[k].decode('utf-8')
        return_to = decoded_params.get('openid.return_to', '')
        info = oidconsumer.complete(decoded_params, return_to)

        session = environ[self.session_middleware]
        if info.status == consumer.FAILURE and info.identity_url:
            session['error'] = "Verification of %s failed." % info.identity_url
        elif info.status == consumer.SUCCESS:
            username = info.identity_url
            if info.endpoint.canonicalID:
                username = info.endpoint.canonicalID
            user_data = sreg.SRegResponse.fromSuccessResponse(info)
            if user_data is not None:
                user_data = user_data.getExtensionArgs()
            if user_data is None:
                user_data = {}
            pape_resp = pape.Response.fromSuccessResponse(info)

            ax_data = ax.FetchResponse.fromSuccessResponse(info)
            if ax_data is not None:
                ax_data = ax_data.getExtensionArgs()
                user_data['ax_data'] = ax_data

            if self.postprocess:
                new_username = self.postprocess(environ, username, user_data)
                if new_username:
                    username = new_username

            # Save user data to session
            session['REMOTE_USER_OPENID'] = username
            session['x-wsgiorg.user_data'] = user_data

            if 'referer' in session:
                redirect_url = session.pop('referer')
            else:
                redirect_url = self.baseurl + self.loggedin_url
            session.save()
            start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', redirect_url)])
            return []
        elif info.status == consumer.CANCEL:
            session['error'] = 'Verification cancelled.'
        elif info.status == consumer.SETUP_NEEDED:
            if info.setup_url:
                session['error'] = 'Setup needed at %s' % info.setup_url
            else:
                session['error'] = 'Setup needed.'
        else:
            session['error'] = info.message
        session.save()

        start_response('301 Redirect', [('Content-type', 'text/html'), ('Location', self.loginurl)])
        return []

    def _get_consumer(self, environ):
        session = environ[self.session_middleware]
        session['id'] = session.id
        oidconsumer = consumer.Consumer(session, self.store)
        session.save()
        return oidconsumer

    def _get_referer(self, environ):
        session = environ[self.session_middleware]
        if 'referer' not in session and 'HTTP_REFERER' in environ:
            referer = environ['HTTP_REFERER']
            mark = referer.find('?')
            if mark == -1:
                mark = 0
            if not referer[:mark].endswith(self.verify_url) and \
                    not referer[:mark].endswith(self.process_url):
                session['referer'] = referer
                session.save()

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


def middleware(app, app_conf=None, prefix='authopenid.', handle_httpexception=True, **options):
    if handle_httpexception:
        app = HTTPExceptionHandler(app)

    if app_conf is None:
        app_conf = {}
    authopenid_conf = load_config(options, app_conf, prefix)

    app = AuthOpenIdHandler(app, app_conf, authopenid_conf)

    return app
