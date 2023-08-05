"""Form and cookie based authentication middleware

As with all the other AuthKit middleware, this middleware is described in
detail in the AuthKit manual and should be used via the
``authkit.authenticate.middleware`` function.
"""

template = """\
<html>
  <head><title>Please Login!</title></head>
  <body>
    <h1>Please Login</h1>
    <form action="%s" method="post">
      <dl>
        <dt>Username:</dt>
        <dd><input type="text" name="username"></dd>
        <dt>Password:</dt>
        <dd><input type="password" name="password"></dd>
      </dl>
      <input type="submit" name="authform" value="Sign In" />
    </form>
  </body>
</html>
"""

from paste.auth.form import AuthFormHandler
from paste.request import construct_url, parse_formvars

class Form(AuthFormHandler):
    def __init__(
        self, 
        app,
        **p
    ):
        AuthFormHandler.__init__(self, app, **p)
    
    def on_authorized(self, environ, start_response):
        environ['paste.auth_tkt.set_user'](userid=environ['REMOTE_USER'])
        return self.application(environ, start_response)
        
    def __call__(self, environ, start_response):
        username = environ.get('REMOTE_USER','')
        if username:
            return self.application(environ, start_response)

        if 'POST' == environ['REQUEST_METHOD']:
            formvars = parse_formvars(environ, include_get_vars=False)
            username = formvars.get('username')
            password = formvars.get('password')
            if username and password:
                if self.authfunc(environ, username, password):
                    environ['AUTH_TYPE'] = 'form'
                    environ['REMOTE_USER'] = username
                    environ['REQUEST_METHOD'] = 'GET'
                    environ['CONTENT_LENGTH'] = ''
                    environ['CONTENT_TYPE'] = ''
                    del environ['paste.parsed_formvars']
                    return self.on_authorized(environ, start_response)

        content = self.template % construct_url(environ)
        start_response("200 OK",[('Content-Type', 'text/html'),
                                 ('Content-Length', str(len(content)))])
        return [content]

