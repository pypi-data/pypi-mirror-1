"""Internal forward middleware for manual authentication handling

For an example of the use of this middleware read the main AuthKit manual or
look at the Pylons example at http://pylonshq.com/project/pylonshq/wiki/PylonsWithAuthKitForward
"""

from paste.recursive import RecursiveMiddleware, ForwardRequestException, CheckForRecursionMiddleware

class Redirect:
    def __init__(self, app, forward_signin):
        self.app = app
        self.signin_path = forward_signin

    def __call__(self, environ, start_response):
        raise ForwardRequestException(self.signin_path)

class MyRecursive:
    def __init__(self, app):
        self.application = app
    def __call__(self, environ, start_response):
        try:
            result = []
            for data in self.application(environ, start_response):
                result.append(data)
            return result
        except ForwardRequestException, e:
            return CheckForRecursionMiddleware(e.factory(self), environ)(environ, start_response)

