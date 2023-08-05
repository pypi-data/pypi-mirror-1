"""AuthKit - authentication and authorisation facilities

(C) James Gardner 2005 MIT Licence see AuthKit.__copyright__
"""

__docformat__ = "restructuredtext"
__copyright__ = """
Copyright (c) 2005 James Gardner <python@jimmyg.org>

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author or contributors may not be used to endorse or
   promote products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""
#~ #__all__ = ['SQLObjectAuthStore','DatabaseAuthStore','AuthError','driver_names']

#~ from extras.time import seconds
#~ import datetime
#~ # Python 2.1 support
#~ try:
    #~ True
    #~ False
#~ except NameError:
    #~ True = 1
    #~ False = 0
    
#~ import time, md5
#~ #import web.auth

#~ def driver_names():
    #~ # XXX Needs to use egg plugins
    #~ return ('DatabaseAuthStore', 'SQLObjectAuthStore', 'SQLAlchemyAuthStore')

class AuthError(Exception):
    """
    Error Class for the Auth Module. 
    
    Use as follows::

        try:
            raise AuthError(ERROR_PASSWORD)
        except AuthError, e:
            print 'Auth exception occurred, value:', e.value
    """
    
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

#~ class IAuthStoreDriver:
    #~ pass

#~ class IAuthStore:

    #~ #
    #~ # Session Functions (These functions do not authorisation or authentication, they just store auth session information
    #~ #

    #~ def authorise(self, username, application='default', role=None, active=1, group=[], signed_in=None, idle_max=None, session_max=None):
        #~ username = username.lower()
        #~ user = self.user(username)
        #~ self._driver_update_accessed(username)
        #~ if active not in [1,0,None]:
            #~ raise AuthError('active can only be True, False or None, not %s'%repr(active))
        #~ #if application != None and level == None and role==None:
        #~ #    raise AuthError('You must specify a role or access level as well as the application')
        #~ if group != []:
            #~ if not self._driver_group_exists(group):
                #~ raise AuthError('No such group %s'%repr(group))
            #~ elif user['group'] != group:
                #~ return False
        #~ if active in [1,0] and user['active'] != active:
            #~ return False
        #~ if role != None and (not user['roles'].has_key(application) or role not in user['roles'][application]):
            #~ return False
        #~ if signed_in != None or session_max != None or idle_max != None:
            #~ is_signed_in = False
            #~ history = self._driver_history(username)
            #~ if history:
                #~ if history[0][0] == None:
                    #~ is_signed_in = True
            #~ if (signed_in == True and is_signed_in == False) or (signed_in == False and is_signed_in == True):
                #~ return False
            #~ if (session_max != None or idle_max != None) and is_signed_in == False:
                #~ return False
            #~ if session_max != None:
                #~ if datetime.datetime(2005,12,12,12).now() - history[0][1] >= datetime.timedelta(seconds=seconds(session_max)):
                    #~ return False
            #~ if idle_max != None:
                #~ if datetime.datetime(2005,12,12,12).now() - history[0][2] >= datetime.timedelta(seconds=seconds(idle_max)):
                    #~ return False
        #~ return True 
    #~ authorize = authorise
    
    #~ def authenticate(self, username, password):
        #~ if not self.user_exists(username):
            #~ return False
        #~ realpassword = self._driver_user(username, property='password')
        #~ if self._encryption == 'md5':
            #~ password = md5.new(password).hexdigest()
        #~ return realpassword == password

    #~ def sign_out(self, username):
        #~ if self.authorise(username, signed_in=1):
            #~ return self._driver_sign_out(username)
            #~ # XXX should return 1 if signed out
        #~ return 0
        
    #~ def sign_in(self, username):
        #~ # XXX should return 1 if signed out
        #~ return self._driver_sign_in(username)

    #~ def history(self, username):
        #~ return self._driver_history(username)

    #~ #
    #~ # Manager Functions
    #~ #

    #~ def user(self, username, property=None):
        #~ if not property:
            #~ user = self._driver_user(username.lower())
            #~ return AuthUser(self, user, self._encryption)
        #~ else:
            #~ return self._driver_user(username.lower(), property)

    #~ #
    #~ # Environment
    #~ #
    
    #~ def create_store(self):
        #~ self._driver_create_store()
        #~ self._driver_add_application(name='default')
        
    #~ def remove_store(self):
        #~ return self._driver_remove_store()
        
    #~ def store_exists(self):
        #~ """Checks whether *all* the components of the auth store exist"""
        #~ return self._driver_store_exists()
        
    #~ #
    #~ # Applications
    #~ #
    
    #~ def applications(self):
        #~ return self._driver_applications()
        
    #~ def application_exists(self, name):
        #~ if not isinstance(name, str):
            #~ raise AuthError('The application name should be a string')
        #~ return self._driver_application_exists(name)
            
    #~ def add_application(self, name):
        #~ if not isinstance(name, str):
            #~ raise AuthError('The application name should be a string')
        #~ if self.application_exists(name):
            #~ raise AuthError("The application '%s' already exists."%name)
        #~ return self._driver_add_application(name)
        
    #~ def remove_application(self, name, unset_roles=False):
        #~ if not isinstance(name, str):
            #~ raise AuthError('The application name should be a string')
        #~ if not self.application_exists(name):
            #~ raise AuthError("The application '%s' doesn't exist in the database."%name)
        #~ return self._driver_remove_application(name, unset_roles)

    #~ #
    #~ # Users
    #~ #
    
    #~ def users(self, group=[], active=None, application=None, role=None):
        #~ if not (isinstance(group, str) or group in [None,[]]):
            #~ raise AuthError('Expected group to be a string, None, or [] to indicate any group, not %s'%repr(group))
        #~ if not (isinstance(role, str) or role==None):
            #~ raise AuthError('Expected role to be a string or None, not %s'%repr(role))
        #~ if not active in [None, True, False]:
            #~ raise AuthError('Expected active to be None, True or False, not %s'%repr(role))
        #~ if not (isinstance(application, str) or application==None):
            #~ raise AuthError('Expected application to be a string or None, not %s'%repr(application))
        #~ if group != [] and group!=None and not self.group_exists(group):
            #~ raise AuthError('No such group %s'%repr(group))
        #~ if application!=None and not self.application_exists(application):
            #~ raise AuthError('No such application %s'%repr(application))
        #~ if role != [] and role!=None and not self.role_exists(role):
            #~ raise AuthError('No such role %s'%repr(role))
        #~ return self._driver_users(group, active, application, role)
        
    #~ def user_exists(self, username):
        #~ return self._driver_user_exists(username.lower())
        
    #~ def add_user(self, username, password='', firstname='', surname='', email='', active=1, group=None): # CHANGED
        #~ if self.user_exists(username):
            #~ raise AuthError('That user already exists.')
        #~ if group != None and not self.group_exists(group):
            #~ raise AuthError('That group doesn\'t exist.')
        #~ for property in [firstname, surname, email, password]:
            #~ if not isinstance(property, str):
                #~ raise AuthError("The params firstname, surname, email, password should all be strings")
        #~ if active not in [True, False ,None]:
            #~ raise AuthError('The param \'active\' can only be True, False or None, not %s'%repr(active))
        #~ if self._encryption == 'md5':
            #~ password = md5.new(password).hexdigest()
        #~ return self._driver_add_user(username.lower(), password, firstname, surname, email, active, group)
        
    #~ def remove_user(self, username):
        #~ return self._driver_remove_user(username.lower())

    #~ def set_user(self, username, **p):
        #~ return self._driver_set_user(username, **p)

    #~ #
    #~ # Roles
    #~ # 
    
    #~ def add_role(self, role):
        #~ if not isinstance(role, str):
            #~ raise AuthError('The application name should be a string')
        #~ if self.role_exists(role):
            #~ raise AuthError("The '%s' role already exists."%role)
        #~ return self._driver_add_role(role)

    #~ def role_exists(self, role):
        #~ if not isinstance(role, str):
            #~ raise AuthError('The application name should be a string')
        #~ return self._driver_role_exists(role)

    #~ def remove_role(self, role, unset_roles=False):
        #~ if not isinstance(role, str):
            #~ raise AuthError('The application name should be a string')
        #~ if not self.role_exists(role):
            #~ raise AuthError("The '%s' role doesn't exist in the database."%role)
        #~ return self._driver_remove_role(role, unset_roles)

    #~ def roles(self, username=None, application=None): # this is correct app shouldn't be default
        #~ if username != None: 
            #~ username = username.lower()
        #~ return self._driver_roles(username, application)

    #~ def has_role(self, username, role, application='default',):
        #~ if username == None or role == None: 
            #~ return False
        #~ else:
            #~ username = username.lower()
            #~ roles = self._driver_roles(username, application)
            #~ return (role in roles)

    #~ def set_group(self, username, group):
        #~ self.user(username.lower()).group = group
        
    #~ def set_role(self, username, role, application='default',):
        #~ username = username.lower()
        #~ roles = role
        #~ if not (isinstance(roles, tuple) or isinstance(roles, list)):
            #~ roles = [roles]
        #~ return self._driver_set_role(username, roles, application)

    #~ def unset_role(self, username, role, application='default'):
        #~ username = username.lower()
        #~ return self._driver_unset_role(username, role, application)
        
    #~ def unset_all_roles(self, username):
        #~ for application, roles in self.user(username).roles.items():
            #~ for role in roles:
                #~ self.unset_role(username, application=application, role=role)

    #~ #
    #~ # Groups
    #~ #

    #~ def group_exists(self, group):
        #~ if not isinstance(group, str):
            #~ raise AuthError('The application name should be a string')
        #~ return self._driver_group_exists(group)
        
    #~ def add_group(self, group):
        #~ if not isinstance(group, str):
            #~ raise AuthError('The application name should be a string')
        #~ if self.group_exists(group):
            #~ raise AuthError("The '%s' group already exists."%group)
        #~ return self._driver_add_group(group)

    #~ def remove_group(self, group, remove_users=False):
        #~ if not isinstance(group, str):
            #~ raise AuthError('The application name should be a string')
        #~ if not self.group_exists(group):
            #~ raise AuthError("The '%s' group doesn't exist in the database."%group)
        #~ return self._driver_remove_group(group, remove_users)
    
    #~ def groups(self):
        #~ return self._driver_groups()
        
#~ def permissions(**kw):
    #~ for key in kw.keys():
        #~ if key not in ['username', 'signed_in', 'idle_max', 'session_max', 'group','role','application']:
            #~ raise AuthError('Invalid permission parameter %s'%repr(key))
    #~ return kw

#~ class AuthUser:
    #~ def __init__(self, driver, user, encryption):
        #~ self.__dict__['_driver']    = driver
        #~ self.__dict__['encryption'] = encryption
        #~ if self.encryption not in [None, 'md5']:
            #~ raise AuthError('Invalid encryption format %s'%self.encryption)
        #~ self.__dict__['username']   = user['username']
        #~ self.__dict__['password']   = user['password']
        #~ self.__dict__['firstname']  = user['firstname']
        #~ self.__dict__['surname']    = user['surname']
        #~ self.__dict__['email']      = user['email']
        #~ self.__dict__['roles']      = user['roles']
        #~ self.__dict__['active']     = user['active']
        #~ self.__dict__['group']      = user['group']
        #~ self.__dict__['history']    = self._driver.history(user['username'])
 
    #~ def __setattr__(self, name, value):
        #~ return self.__setitem__(name, value)

    #~ def __setitem__(self, name, value):
        #~ if name in ['firstname', 'surname', 'email', 'group', 'active']:
            #~ p = {name:value}
            #~ # Set in the database
            #~ self._driver._driver_set_user(self.username, **p) 
            #~ # Set in the class
            #~ self.__dict__[name] = value 
        #~ elif name == 'password':
            #~ if self.encryption == 'md5':
                #~ value = md5.new(value).hexdigest()
            #~ p = {name:value}
            #~ # Set in the database
            #~ self._driver._driver_set_user(self.username, **{name:value}) 
            #~ # Set in the class
            #~ self.__dict__[name] = value 
        #~ else:
            #~ if name in self.__dict__.keys():
                #~ raise AttributeError('You cannot set the value of the %s attribute'%name)
            #~ else:
                #~ raise AttributeError('No such attribute %s'%name)

    #~ def __getitem__(self, name):
        #~ if name in ['firstname', 'surname', 'email', 'group', 'active', 'password', 'roles', 'history']:
            #~ return getattr(self, name)
        #~ raise KeyError('No such key %s'%name)
    
#~ class AuthStore(IAuthStore, IAuthStoreDriver):
    #~ def __init__(self, encryption=None):
        #~ self._store_exists = self.store_exists()
        #~ self._encryption = encryption
        #~ if self._encryption not in [None, 'md5']:
            #~ raise AuthError('Invalid encryption format %s'%self._encryption)

#~ from authkit.drivers.SQLObject_driver import SQLObjectAuthStore, connectionForURI

#~ from authkit.drivers.database import DatabaseAuthStore
#~ from authkit.controllers import *
