"""Highly flexible OpenID based authentication middleware

.. Note::
    
    "Passurl" is a trademark of James Gardner 2005.

    If you want to test this module feel free to setup an account at
    passurl.com. The site is in alpha and any accounts will be deleted before
    launch but it might help with testing.

Full documentation on the use of this OpenID module is in the AuthKit manual.
"""

# TODO: Package up the OpenID Libraries into an egg so they don't need
# installing manually


import cgi
import paste.request
import string
import sys
from authkit.authenticate import AuthKitConfigError
from paste.request import construct_url

try:
    from openid.consumer import consumer
    from openid.oidutil import appendArgs
    from yadis.discover import DiscoveryFailure
    from urljr.fetchers import HTTPFetchingError
except ImportError:
    raise Exception("Could not import all the requried OpenID libraries. Have you manually installed them?")

template = """\
<html>
  <head><title>Please Sign In</title></head>
  <body>
    <h1>Please Sign In</h1>
    <div class="$css_class">$message</div>
    <form action="$action" method="post">
      <dl>
        <dt>Passurl:</dt>
        <dd><input type="text" name="passurl" value="$value"></dd>
      </dl>
      <input type="submit" name="authform" />
      <hr />
    </form>
  </body>
</html>
"""

def passurl_urltouser(environ, url):
    return url.strip('/').split('/')[-1]

def render(template, **p):
    if sys.version_info >= (2,4):
        return string.Template(template).substitute(
            **p
        )
    else:
        for k, v in p.items():
            template = template.replace('$'+k, v)
        return template

class PassURLSignIn:
    """
    This middleware is triggered when the authenticate middleware catches a 401 response
    
    The form is submitted to the verify URL which the other middleware handles
    """
    def __init__(self, app, template, path_verify, baseurl=''):
        self.app = app
        self.template = template
        self.baseurl = baseurl
        self.path_verify = path_verify

    def __call__(self, environ, start_response):
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)
        # XXX For registration support this should render hidden fields with the sreg options
        content = render(
            self.template,
            message='',
            value='',
            css_class='',
            action=baseurl + self.path_verify
        )
        start_response(
            "200 OK",
            [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(content)))
            ]
        )
        return [content]

def make_store(store, config):
    conn = None
    if store == 'file':
        from openid.store import filestore
        cstore = filestore.FileOpenIDStore(config)
    elif store == 'mysql':
        import MySQLdb
        from DBUtils.PersistentDB import PersistentDB
        from openid.store.sqlstore import MySQLStore
        from sqlalchemy.engine.url import make_url
        
        def create_conn(dburi):
            url = make_url(dburi)
            p={'db':url.database}
            if url.username:
                p['user'] = url.username
            if url.password:
                p['passwd'] = url.password
            if url.host:
                p['host'] = url.host
            if url.port:
                p['port'] = url.port
            return PersistentDB(MySQLdb, 1, **p).connection()
        conn = create_conn(config)
        cstore = MySQLStore(conn)
    else:
        raise Exception("Invalid store type %r"%store)
    return conn, cstore
    
    
class AuthOpenIDHandler:
    """
    The template should be setup from authkit.passurl.template.file or authkit.passurl.template.obj before we get here!
    """
    def __init__(
        self, 
        app, 
        store_type, 
        store_config, 
        baseurl, 
        path_signedin, 
        template=None,
        session_secret=None,
        session_key='authkit_passurl',
        session_middleware='beaker.session',
        path_verify='/verify', 
        path_process='/process',
        urltouser=None,
    ):
        self.conn, self.store = make_store(store_type, store_config)
        self.baseurl = baseurl
        self.template = template
        #self.path_signin = path_signin
        self.path_signedin = path_signedin
        self.path_verify = path_verify
        self.path_process = path_process
        self.session_middleware = session_middleware
        self.session_key = session_key
        self.session_secret = session_secret
        self.app = app
        self.urltouser = urltouser
                
    def __call__(self, environ, start_response):
        # If we are called it is because we want to sign in, so show the 
        if not environ.has_key(self.session_middleware):
            raise AuthKitConfigError(
                'The session middleware %r is not present. '
                'Have you set up the session middleware?'%(
                    self.session_middleware
                )
            )
        if environ.get('PATH_INFO') == self.path_verify:
            response = self.verify(environ, start_response)
            environ[self.session_middleware].save()
            return response
        elif environ.get('PATH_INFO') == self.path_process:
            response = self.process(environ, start_response)
            environ[self.session_middleware].save()
            return response
        else:
            return self.app(environ, start_response)

    def verify(self, environ, start_response):
    	# XXX This method should accept sreg options and continue with them
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)
        params = dict(paste.request.parse_formvars(environ))
        openid_url = params.get('passurl')
        if not openid_url:
            response = render(
                self.template,
                message='Enter an identity URL to verify.',
                value='',
                css_class='',
                action=baseurl + self.path_verify
            )
            start_response(
                '200 OK', 
                [
                    ('Content-type', 'text/html'),
                    ('Content-length', len(response))
                ]
            )
            return response
        oidconsumer = self._get_consumer(environ)
        try:
            request_ = oidconsumer.begin(openid_url)
        except HTTPFetchingError, exc:
            response = render(
                self.template,
                message='Error retrieving identity URL: %s' % (
                    cgi.escape(str(exc.why))
                ),
                value=self._quoteattr(openid_url),
                css_class='error',
                action=baseurl + self.path_verify
            )
            start_response(
                '200 OK', 
                [
                    ('Content-type', 'text/html'),
                    ('Content-length', len(response))
                ]
            )
            return response
        except DiscoveryFailure, exc:
            response = render(
                self.template,
                message='Error retrieving identity URL: %s' % (
                    cgi.escape(str(exc[0]))
                ),
                value=self._quoteattr(openid_url),
                css_class='error',
                action=baseurl + self.path_verify
            )
            start_response(
                '200 OK', 
                [
                    ('Content-type', 'text/html'),
                    ('Content-length', len(response))
                ]
            )
            return response
        else:
            if request_ is None:
                response = render(
                    self.template,
                    message='No OpenID services found for <code>%s</code>' % (
                        cgi.escape(openid_url),
                    ),
                    value=self._quoteattr(openid_url),
                    css_class='error',
                    action=baseurl + self.path_verify
                )
                start_response(
                    '200 OK', 
                    [
                        ('Content-type', 'text/html'),
                        ('Content-length', len(response))
                    ]
                )
                return response
            else:
                trust_root = baseurl
                return_to = baseurl + self.path_process
                redirect_url = request_.redirectURL(trust_root, return_to)
                start_response(
                    '301 Redirect', 
                    [
                        ('Content-type', 'text/html'),
                        ('Location', redirect_url)
                    ]
                )
                return []

    def process(self, environ, start_response):
        baseurl = self.baseurl or construct_url(environ, with_query_string=False, with_path_info=False)
        value = ''
        css_class = 'error'
        message = ''
        params = dict(paste.request.parse_querystring(environ))
        oidconsumer = self._get_consumer(environ)
        info = oidconsumer.complete(dict(params))
        css_class = 'error'
        if info.status == consumer.FAILURE and info.identity_url:
            fmt = "Verification of %s failed."
            message = fmt % (cgi.escape(info.identity_url),)
            environ['wsgi.errors'].write("PassURL Message: %s %s"%(message,info.message))
        elif info.status == consumer.SUCCESS:
            username = info.identity_url
            # Set the cookie
            if self.urltouser:
                username = self.urltouser(environ, info.identity_url)
            environ['paste.auth_tkt.set_user'](username)
            # Return a page that does a meta refresh
            response = """
<HTML>
<HEAD>
<META HTTP-EQUIV="refresh" content="0;URL=%s">
<TITLE>Signed in</TITLE>
</HEAD>
<BODY>
<!-- You are sucessfully signed in. Redirecting... -->
</BODY>
</HTML>
            """ % (self.baseurl + self.path_signedin)
            start_response(
                '200 OK', 
                [
                    ('Content-type', 'text/html'),
                    ('Content-length', len(response))
                ]
            )
            return response
        elif info.status == consumer.CANCEL:
            message = 'Verification cancelled'
        else:
            environ['wsgi.errors'].write("PassURL Message: %s"%info.message)
            message = 'Verification failed.'
        value = self._quoteattr(info.identity_url)
        response = render(
            self.template,
            message=message,
            value=value,
            css_class=css_class,
            action=baseurl + self.path_verify
        )
        start_response(
            '200 OK', 
            [
                ('Content-type', 'text/html'),
                ('Content-length', len(response))
            ]
        )
        return response

    #
    # Helper methods
    #

    def _get_consumer(self, environ):
        session = environ[self.session_middleware]
        session['id'] = session.id
        return consumer.Consumer(session, self.store)

    def _quoteattr(self, s):
        if s == None:
            s = ''
        qs = cgi.escape(s, 1)
        return '"%s"' % (qs,)
    
