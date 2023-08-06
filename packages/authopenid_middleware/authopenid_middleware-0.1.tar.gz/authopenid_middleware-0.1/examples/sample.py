#!/usr/bin/env python

import authopenid_middleware
from beaker.middleware import SessionMiddleware
from authorize_middleware.pylons_func import authorize_request
import cgi

login_template = '<html><head><title>Please Sign In</title></head>'\
    '<body><h1>Please Sign In</h1>'\
    '<div>%s</div>'\
    '<form action="/verify" method="post">'\
    '<label>OpenID:</label>'\
    '<input type="text" name="openid">'\
    '<input type="submit"/>'\
    '</form>'\
    '</body>'\
    '</html>'

class SampleApp:

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        """
        A sample WSGI application that returns a 401 status code when the path 
        ``/private`` is entered, triggering the authenticate middleware to 
        prompt the user to sign in.

        ``/logout`` will display a signed out message.

        ``/login`` should display the sign in form.

        The path ``/`` always displays the environment.
        """
        if environ['PATH_INFO']=='/private':
            authorize_request(environ)
        if environ['PATH_INFO'] == '/logout':
            start_response('200 OK', [('Content-type', 'text/plain; charset=UTF-8')])
            if environ.has_key('REMOTE_USER'):
                return ["Signed Out"]
            else:
                return ["Not signed in"]
        elif environ['PATH_INFO'] == '/login':
            session = environ['beaker.session']
            error = ''
            if session.get('error'):
                error = session.pop('error')
                session.save()
            start_response('200 OK', [('Content-type', 'text/html; charset=UTF-8')])
            return [login_template % cgi.escape(error)]
        else:
            start_response('200 OK', [('Content-type', 'text/plain; charset=UTF-8')])
        result = ['You Have Access To This Page.\n\nHere is the environment...\n\n']
        for k,v in environ.items():
            result.append('%s: %s\n'%(k,v))
        return result

if __name__ == '__main__':
    from paste.httpserver import serve
    app = authopenid_middleware.middleware(SampleApp(),
            ax_required='http://schema.openid.net/contact/email')
    app = SessionMiddleware(
        app, 
        key='authopenid', 
        secret='secret',
    )

    serve(app, host='0.0.0.0', port=8080)
