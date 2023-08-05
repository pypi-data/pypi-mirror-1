from paste.auth.auth_tkt import make_auth_tkt_middleware
from paste.recursive import RecursiveMiddleware, ForwardRequestException

class ShowSignInOn403:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        def authkit_start_response(status, headers, exc_info=None):
            if status[:3] == '403':
                status = '401 Access was denied. Please sign in.'
            return start_response(status, headers, exc_info)
        return self.app(environ, authkit_start_response)

class RedirectOn401:
    def __init__(self, app, signin_path):
        self.app = app
        self.signin_path = signin_path
    def __call__(self, environ, start_response):
        def authkit_start_response(status, headers, exc_info=None):
            if status[:3] == '401':
                raise ForwardRequestException(self.signin_path)
            return start_response(status, headers, exc_info)
        return self.app(environ, authkit_start_response)

def authkit_form(
    app, 
    global_conf,
    secret='session_secret',
    cookie_name='auth_tkt',
    secure=False,
    include_ip=True,
    sign_out_path='account/signout',
    sign_in_path='account/signin',
):
    app = make_auth_tkt_middleware(app,global_conf,secret,cookie_name,secure,include_ip,sign_out_path)
    app = RecursiveMiddleware(app, global_conf)
    app = ShowSignInOn403(app) 
    app = RedirectOn401(app, sign_in_path)
    return app
    