"""Authorization objects for checking permissions

In the AuthKit model permissions are handled by ``Permission`` objects.
Authorization objects are used to check permissions and to raise
``NotAuthenticatedError`` or ``NotAuthorizedError`` if there is no user or the
user is not authorized. The execeptions are converted to HTTP responses which
are then intercepted and handled by the authentication middleware.

The way permissions objects should be checked depends on where abouts in the
application stack the check occurs and so different authorization objects exist
to make checks at different parts of the stack. You can of course create 
your own permission objects to be authorized by the middleware and decorator
defined here. See the permissions docs or the AuthKit manual for more 
information.

Framework implementors might also create their own implementations of AuthKit
authorization objects. For example the ``authkit.pylons_adaptors`` module
contains some Pylons-specific authorization objects which you'll want to use
if you are using AuthKit with Pylons.

For an example of how to use permission objects have a look at the
``AuthorizeExampleApp`` class in the ``authorize.py`` example in the ``examples``
directory or have a look at the AuthKit manual.
"""

from paste import httpexceptions

#
# Errors
#

class PermissionError(httpexceptions.HTTPClientError):
    """
    Base class from which ``NotAuthenticatedError`` and ``NotAuthorizedError`` 
    are inherited.
    """
    pass

class NotAuthenticatedError(PermissionError):
    """
    Raised when a permission check fails because the user is not authenticated.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``401`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    required_headers = ()
    code = 401
    title = 'Not Authenticated'

class NotAuthorizedError(PermissionError):
    """
    Raised when a permission check fails because the user is not authorized.

    The exception is caught by the ``httpexceptions`` middleware and converted into
    a ``403`` HTTP response which is intercepted by the authentication middleware
    triggering a sign in.
    """
    code = 403
    title = 'Forbidden'
    explanation = ('Access was denied to this resource.')

class NonConformingPermissionError(Exception):
    """
    Raised when a custom permission object is not behaving in a compliant way
    """
    pass

#
# Authorize Objects
#

class _Authorize:
    def __init__(self, app, permission):
        self.app = app
        self.permission = permission

    def __call__(self, environ, start_response):
        # Could also check that status and response haven't changed here?
        try:
            return self.permission.check(self.app, environ, start_response)
        except NotAuthenticatedError:
            if environ.has_key('REMOTE_USER'):
                raise NonConformingPermissionError(
                    'Faulty permission: NotAuthenticatedError raised '
                    'but REMOTE_USER key is present.'
                )
            else:
                raise

class _PermissionStartResponse:
    def __init__(self, status, headers, exc_info=None):
        pass
        
def middleware(app, permission):
    """
    Returns an WSGI app wrapped in authorization middleware and on each request
    will check the permission specified.

    Takes the arguments:

    ``app``
        The WSGI application to be wrapped

    ``permission``
        The AuthKit permission object to be checked.

    The ``httpexceptions`` and ``authkit.authenticate.middleware`` middleware need to
    be wrap this middleware otherwise any errors triggered will not be intercepted.

    See the AuthKit manual for an example.
    """
    return _Authorize(app, permission)

def authorize(permission):
    """
    This is an authorize decorator (requires Python 2.4) which can be used
    to decorate a function. It takes the permission to check as its only 
    argument.

    See the AuthKit manual for an example.
    """
    def decorate(func):
        def input(self, environ, start_response):
            def app(environ, start_response):
                return func(self, environ, start_response)
            return permission.check(app, environ, start_response)
        return input
    return decorate

