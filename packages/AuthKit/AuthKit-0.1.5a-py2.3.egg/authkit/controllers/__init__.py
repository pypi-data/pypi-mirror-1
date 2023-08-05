import pylons
import types
import formbuild
from authkit.middleware import UsernameSigner, SimpleCookie
from authkit.validators import BasicRegistration
import formencode
import authkit, formencode
from authkit.validators import BasicRegistration


class State:
    pass
    
class PylonsBaseSecureController(pylons.Controller):
    
    authname = 'auth'
    
    def __call__(self, action, **kargs):
        kargs['action'] = action
        if hasattr(self, '__before__'):
            self._inspect_call(self.__before__, **kargs)
        if isinstance(getattr(self, kargs['action'], None), types.MethodType):
            # Default is that if a permissions attribute is specified then it isn't public
            if self.__granted__(action):
                func = getattr(self, kargs['action'])
                self._inspect_call(func, **kargs)
            else:
                raise Exception('Call to __security__ failed to halt the request')
        else:
            if pylons.request.environ['paste.config']['default']['debug'] == 'false':
                pylons.m.abort(404, "File not found")
            else:
                raise NotImplementedError('Action %s is not implemented'%action)
        if hasattr(self, '__after__'):
            self._inspect_call(self.__after__, **kargs)
            
    def __granted__(self, action):
        action_ = getattr(self, action)
        if hasattr(action_, 'permissions'):            
            if not pylons.request.environ.has_key('paste.login.http_login'):
                raise Exception('Action permissions specified but security middleware not present.')
            if pylons.request.environ.has_key('REMOTE_USER'):
                if self.__authorize__(pylons.request.environ['REMOTE_USER'], action_.permissions):
                    return True
                else:
                    pylons.m.abort(403, 'Access Denied')
            else:
                pylons.m.abort(401, 'Not signed in')
        else:
            return True

    def __authorize__(self, user, permissions):
        return False
        
    def __signout__(self, username):
        from authkit.middleware import SimpleCookie
        cookie = SimpleCookie(
            pylons.request.environ['paste.login.cookie_name'],
            '',
            '/',
        )
        pylons.request.headers_out['Set-Cookie'] = str(cookie)
        pylons.request.environ['REMOTE_USER'] = ''
        
    def __signin__(self, username):
        from authkit.middleware import SimpleCookie
        cookie = SimpleCookie(
            pylons.request.environ['paste.login.cookie_name'],
            pylons.request.environ['paste.login.signer'].make_signature(username),
            '/',
        )
        pylons.request.headers_out['Set-Cookie'] = str(cookie)
        pylons.request.environ['REMOTE_USER'] = username

from pylons import request
class PylonsSecureController(PylonsBaseSecureController):
    
    def __signout__(self, username):
        g = request.environ['pylons.g']
        getattr(g,self.authname).sign_out(username=username)
        PylonsBaseSecureController.__signout__(self, username)
        
    def __signin__(self, username):
        g = request.environ['pylons.g']
        getattr(g,self.authname).sign_in(username=username)
        PylonsBaseSecureController.__signin__(self, username)

    def __authorize__(self, signed_in_user, ps):
        permissions = {}
        g = request.environ['pylons.g']
        for k,v in ps.items():
            permissions[k]=v
        def valid():
            if permissions.has_key('username'):
                if signed_in_user.lower() != permissions['username'].lower():
                    return False
            else:
                permissions['username'] = signed_in_user
            if not getattr(g,self.authname).user_exists(permissions['username']):
                return False
            else:
                return getattr(g,self.authname).authorise(**permissions)
        if valid():
            return True
        else:
            self.__signout__(permissions['username'])
            return False

