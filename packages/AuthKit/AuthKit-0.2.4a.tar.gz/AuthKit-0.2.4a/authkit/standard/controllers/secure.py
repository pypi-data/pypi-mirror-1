import types
import sqlalchemy.mods.threadlocal
import sqlalchemy
from pylons import request, c, h, Response
from pylons.controllers import WSGIController

class SecureController(WSGIController):
 

    def __call__(self, environ, start_response):
        match = environ['pylons.routes_dict']
            
    #def __call__(self, **params):
        self.model.meta.connect(request.environ['paste.config']['app_conf']['dsn'])
        #sqlalchemy.global_connect(request.environ['paste.config']['app_conf']['dsn'])
        sqlalchemy.objectstore.clear()
        
        env = {}
        for k,v in request.environ.items():
            env[k]=v
        env['SCRIPT_NAME'] = ''
        import routes
        config = routes.request_config()
        config.environ = env
        if not isinstance(getattr(self, match.get('action'), None), types.MethodType):
            if request.environ['paste.config']['global_conf']['debug'] == 'false':
                abort(404)
                #abort(404, "File not found")
            else:
                raise NotImplementedError('Action %s is not implemented'%match.get('action'))
        granted, result = self.__granted__(match.get('action'))
        if granted:
            result = WSGIController.__call__(self, environ, start_response)
        #else:
        #    return response
        sqlalchemy.objectstore.flush()
        return result
            
    def __granted__(self, action):
        action_ = getattr(self, action)
        if not request.environ.has_key('paste.auth_tkt.set_user') or not request.environ.has_key('paste.auth_tkt.logout_user'):
            raise Exception('auth_tkt middleware not present.')
        if request.environ.has_key('REMOTE_USER'):
            user = self.model.User.mapper.select_by(username=request.environ['REMOTE_USER'])
            if not len(user):
                h.log(
                    '%s: User %s specified in REMOTE_USER does not exist in AuthKit database'%(
                        self.__class__.__name__,
                        request.environ['REMOTE_USER']
                    )
                )
                if hasattr(action_, 'permissions'):
                    return [False, Response(code=401)]#m.abort(401, 'Access Denied - Invalid user. See logs for more information.')
                else:
                    return [True, None]
            user = user[0]
            user.histories[0].last_accessed = self.model.now()
            request.environ['authkit.user'] = user
            if hasattr(action_, 'permissions'):
                if action_.permissions():
                    return [True, None]
                else:
                    return [False, Response(code=403)]
                    #m.abort(403, 'Access Denied')
            else:
                return [True, None]
        else:
            if hasattr(action_, 'permissions'):
                return [False, Response(code=401)]
                #m.abort(401, 'Not signed in')
            else:
                return [True, None]


    def __signout__(self, username, response):
        user = self.model.User.mapper.select_by(username=username)[0]
        now = self.model.now()
        for history in user.current_sessions:
            if history.signed_out == None:
                history.signed_out = now
        # Old version: request.headers_out['Set-Cookie'] = 'auth_tkt=""; Path=/'
        #response.delete_cookie('auth_tkt')
        response.set_cookie('auth_tkt')
        # def set_cookie(self, key, value='', max_age=None, expires=None, path='/', domain=None, secure=None):
   
        # This fails because it sets multiple cookies and then the user can't sign in again
        # request.environ['paste.auth_tkt.logout_user']()
        
        
    def __signin__(self, username):
        # This fails because it sets multiple cookies and then the user can't sign in again
        # request.environ['paste.auth_tkt.logout_user']()
        #g = request.environ['pylons.g']
        # Only a signed in user that existed would get this far so we can use [0]
        user = self.model.User.mapper.select_by(username=username)[0]
        now = self.model.now()
        for history in user.current_sessions:
            if history.signed_out == None:
                history.signed_out = now
        user.histories.append(self.model.History(last_accessed=now))
        request.environ['paste.auth_tkt.set_user'](username)
