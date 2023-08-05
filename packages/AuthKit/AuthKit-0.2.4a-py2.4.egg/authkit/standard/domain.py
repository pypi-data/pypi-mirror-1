
#
# Domain objects
#

class User(object):
    def __init__(self, uid=None, username=None, password=None, firstname=None, surname=None, email=None, group_uid=None, active=None, session=None):
        self.uid = uid
        self.username = username
        #if user <> None:
        #    self._user = user.lower()
        # user ids have to be lowercase. This is enforced here.
        #def _set_user(self, user):
        #    self._user = user.lower()
        #def _get_user(self, user):
        #    return self._user
        #user = property(_get_user, _set_user)
    
        
        self.password = password
        self.firstname = firstname
        self.surname = surname
        #self.email = email
        self.active = active
        self.group_uid = group_uid
        self.session = session

class App(object):
    def __init__(self, name=None):
        self.name = name
        
class Role(object):
    def __init__(self, name=None):
        self.name = name
        
class Group(object):
    def __init__(self, name=None):
        self.name = name
    
#~ class Usergroup(object):
    #~ def __init__(self, user=None, group=None):
        #~ self.user = user
        #~ self.group = group
        
class Permission(object):
    def __init__(self, user_uid=None, app_uid=None, role_uid=None):
        self.user_uid = user_uid
        self.app_uid = app_uid
        self.role_uid = role_uid

class History(object):
    def __init__(self, username=None, signed_in=None, last_accessed=None, signed_out=None):
        self.username = username
        self.signed_in = signed_in
        self.last_accessed = last_accessed
        self.signed_out = signed_out
