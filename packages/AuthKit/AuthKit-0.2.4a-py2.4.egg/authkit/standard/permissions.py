from pylons import request, h
import md5, random, time, base64, datetime

# 
# Permission Classes
#

class Permissions:
    def __call__(self):
        return False
        
class UserAndHasPermission(Permissions):
    def __init__(self, model, app=None, role=None):
        if app == None and role == None:
            raise Exception('Please specify a role or an application or both')
        self.model = model
        self.app = app
        self.role = role
        self.errors = []

    def __call__(self):
        self.errors = []
        if not request.environ.has_key('authkit.user'):
            self.errors.append('No user signed in')
            return False
            
        if self.app:
            apps = self.model.App.mapper.select_by(name=self.app)
            if not len(apps):
                raise Exception('No such app named %s'%self.app)
            app = apps[0].uid
        
        if self.role:
            roles = self.model.Role.mapper.select_by(name=self.role)
            if not len(roles):
                raise Exception('No such role named %s'%self.role)
            role = roles[0].uid
        
        for permission in request.environ['authkit.user'].permissions:
            if self.role and self.app and permission.role == role and permission.app == app:
                return True
            elif self.role and self.app == None and permission.role == role:
                return True
            elif self.app and self.role == None and permission.app == app:
                return True
            self.errors.append('Appropriate permissions not present')
            return False
    
class Group(Permissions):
    def __init__(self, model, group):       
        self.model = model
        self.group = group

    def __call__(self):
        if not request.environ.has_key('authkit.user'):
            return False
            
        groups = self.model.Group.mapper.select_by(name=self.group)
        if not len(groups):
            raise Exception('No such group named %s'%self.group)
        group = groups[0].uid

        if group == request.environ['authkit.user'].group:
            return True
        return False
        
class UserIn(Permissions):
    def __init__(self, users):
        if isinstance(users, list):
            users_ = []
            for user in users:
                users_.append(user.lower())
            self.users = users_
        elif isinstance(users, str):
            self.users = [users]
        else:
            raise Exception('Expected users to be a list or a string, not %r'%users)

    def __call__(self):
        if not request.environ.has_key('authkit.user'):
            return False
        if request.environ['authkit.user'].user.lower() in self.users:
            return True
        return False

class SignedIn(Permissions):
    def __call__(self):
        if request.environ.has_key('authkit.user'):
            return True
        return False
        
class ValidSession(Permissions):
    def __init__(self):
        self.errors = []
        
    def __call__(self):
        self.errors = []
        if not request.environ.has_key('authkit.user'):
            self.errors.append('No user signed in')
            return False
        user=request.environ['authkit.user']
        expire_time = user.current_sessions[0].signed_in + datetime.timedelta(
            seconds=h.seconds('%smins'%user.session)
        )
        if datetime.datetime.now() > expire_time:
            self.errors.append('Session expired')
            return False
        else:
            return True
        
class And(Permissions):
    def __init__(self, *k):
        self.items = k
        self.errors = []

    def __call__(self):
        self.errors = []
        for k in self.items:
            if not k():
                for error in k.errors:
                    self.errors.append('%s: %s'%(k.__class__.__name__, error))
                return False
        return True

class Or(Permissions):
    def __init__(self, *k):
        self.items = k

    def __call__(self):
        for k in self.items:
            if k():
                return True
        return False

class Not(Permissions):
    def __init__(self, k):
        self.k = k

    def __call__(self):
        return not self.k()
        