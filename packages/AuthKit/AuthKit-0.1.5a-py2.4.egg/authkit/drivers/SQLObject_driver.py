#
# Copyright (c) James Gardner <james@jimmyg.org> 2002-2005 All Rights Reserved
# Licensed under LGPL
#

"""SQLObject driver for AuthKit.

Developer Notes:

* User columns are named ``user`` rather than ``username`` to avoid problems with Gadfly
* The Group column is named ``grp`` rather than ``group`` to avoid confusion with SQL ``GROUP BY``
"""

from authkit import AuthError, AuthStore
import datetime
from sqlobject import SQLObject, StringCol, BoolCol, ForeignKey, MultipleJoin, DateTimeCol, connectionForURI

try:
    True
    False
except NameError:
    True = 1==1
    False = 0==1

class SQLObjectAuthStore(AuthStore):
    """
    An auth store which uses `SQLObject <http://www.sqlobject.org>`_ to store auth information in 
    an SQL database.
    
    
    ``SQLObjectAuthStore`` is used as follows::
    
        >>> from authkit.drivers.SQLObject_driver import SQLObjectAuthStore
        >>> from SQLObject import *
        >>> connection = connectionForURI(connection_string)
        >>> auth = SQLObjectAuthStore(connection=connection)

    """

    def __init__(self, connection, table_prepend='', **auth_store_params):
        self.connection = connection
        self._table_prepend = table_prepend

        class User(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'User'
            _connection = self.connection
            user = StringCol()
            password = StringCol()
            firstname = StringCol()
            surname = StringCol()
            email = StringCol()
            active = BoolCol()
            grp = ForeignKey(self._table_prepend+'Group_')
            # SQLObject Joins
            roles = MultipleJoin(self._table_prepend+'Roles')
            history = MultipleJoin(self._table_prepend+'History')
            
        class App(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'App'
            _connection = self.connection
            name = StringCol()
            roles = MultipleJoin(self._table_prepend+'Roles')
        
        class Group_(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'Group_'
            _connection = self.connection
            name =  StringCol()
            users = MultipleJoin(self._table_prepend+'User')
            
        class Role(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'Role'
            _connection = self.connection
            name =  StringCol()
            roles = MultipleJoin(self._table_prepend+'Roles')
            
        class Roles(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'Roles'
            _connection = self.connection
            user =  ForeignKey(self._table_prepend+'User')
            application = ForeignKey(self._table_prepend+'App')
            role = ForeignKey(self._table_prepend+'Role')

        class History(SQLObject):
            class sqlmeta:
                table = self._table_prepend+'History'
            _connection = self.connection
            user = ForeignKey(self._table_prepend+'User')
            signed_in = DateTimeCol()
            last_accessed = DateTimeCol()
            signed_out = DateTimeCol()
            
        self.tables = {
            'User':User,
            'App':App,
            'Group_':Group_,
            'Role':Role,
            'Roles':Roles,
            'History':History,
        }
            
        AuthStore.__init__(self, **auth_store_params)

#
# Change Store
#
    
    def _driver_create_store(self):
        """
        Destroy any existing store and create the auth store.
        
        If any errors are generated when creating the store an ``authkit.AuthError`` is raised.
        
        After this method is called, the default application is added, you don't need to implement any code for this.
        """

        for name, table in self.tables.items():
            fullname = self._table_prepend+name
            if self.connection.tableExists(fullname):
                raise AuthError('The table %s already exists'%repr(fullname))
            else:
                table.createTable()

    def _driver_remove_store(self):
        """
        Remove the auth store, destroying any data it contains. If there are no problems, ``[]`` is returned.
        
        If any errors occurs preventing the store from being removed an ``authkit.AuthError`` is raised. 
        If the store doesn't exist or only partially exists, any warnings are returned as a list of strings.
        """
        errors = []
        for name, table in self.tables.items():
            fullname = self._table_prepend+name
            if not self.connection.tableExists(fullname):
                errors.append('The table %s doesn\'t exist'%repr(fullname))
            else:
                table.dropTable()
        return errors
        
    def _driver_store_exists(self):
        """
        Returns ``True`` if every component of the store exists, ``False`` otherwise.
        
        Typically used as follows::
        
            if not auth.store_exists():
                try:
                    warnings = auth.remove_store()
                    if warnings:
                        print warnings
                except AuthError:
                    print "Failed"
                    raise
                else:
                    auth.create_store()
                    print "Success"
        """
        for name, table in self.tables.items():
            if not self.connection.tableExists(self._table_prepend+name):
                return False
        return True

#
# Get Objects
#
    
    def _driver_applications(self):
        """
        Return a list of applications in the store, including the ``default`` application.
        """
        return tuple([obj.name for obj in self.tables['App'].select()])

    def _driver_groups(self):
        return tuple([obj.name for obj in self.tables['Group_'].select()])
        
    def _driver_users(self, group=[], active=None, application=None, role=None):
        """
        Return a list of current usernames according to various options
        
        ``group`` 
            Can be ``None`` to select the group of users where no group is assigned
            Can be ``[]`` to select evey user regardless of group
            or can be the name of a group to select just users in that group

        ``active``
            Can be ``None`` to select all users, ``True`` to select users with active accounts
            or ``False`` to select users with disabled accounts
            
        ``application`` 
            Can be ``None`` to select all users reardless of the appliaction they have roles with or the
            application name to select users associated with that application
        
        ``role`` 
            Can be ``None`` to select all users reardless of roles or the
            name of a role to select users with that role
            
        All options are used in combination so to select users of the ``default`` application
        with the role ``editor`` for example you could specify ``application='default', role='editor'`` in the 
        parameters.
        
        Users are returned in alphabetical order.
        """
        rows = []
        #~ if (application==None and role!= None) or (application != None and role == None):
            #~ #raise Exception(application, role)
            #~ raise AuthError('You must specify both role and application or neither of them')

        if application == None and role == None:
            if group == []: # ie all
                if active == None:
                    objs = self.tables['User'].select()
                else:
                    objs = self.tables['User'].selectBy(active=active)
            else:
                if active == None:
                    if group == None:
                        group_ = None
                    else:
                        group_ = self.tables['Group_'].selectBy(name=group).getOne()
                    objs = self.tables['User'].selectBy(grp=group_)
                else:
                    if group == None:
                        group_ = None
                    else:
                        group_ = self.tables['Group_'].selectBy(name=group).getOne()
                    objs = self.tables['User'].selectBy(active=active, group=group_)
        elif application==None and role != None:
            if group == []: # ie all
                roles = self.tables['Role'].selectBy(name=role)
                roles = self.tables['Roles'].selectBy(role=roles.getOne())
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if active == None:
                            objs.append(role.user)
                        elif role.user.active == active:
                            objs.append(role.user)
            else:
                role_ = self.tables['Role'].selectBy(name=role).getOne()
                roles = self.tables['Roles'].selectBy(role=role_)
                if group == None:
                    group_ = None
                else:
                    group_ = self.tables['Group_'].selectBy(name=group).getOne()
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if role.user.grp == group_:
                            if active == None:
                                objs.append(role.user)
                            elif role.user.active == active:
                                objs.append(role.user)
                    else:
                        print group
                                
        elif role==None and application != None:
            application_ = self.tables['App'].selectBy(name=application).getOne().id
            if group == []: # ie all
                apps = self.tables['App'].selectBy(name=application)
                roles = self.tables['Roles'].selectBy(application=apps.getOne())
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if active == None:
                            objs.append(role.user)
                        elif role.user.active == active:
                            objs.append(role.user)
            else:
                if group == None:
                    group_ = None
                else:
                    group_ = self.tables['Group_'].selectBy(name=group).getOne()
                apps = self.tables['App'].selectBy(name=application)
                roles = self.tables['Roles'].selectBy(application=apps.getOne())
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if role.user.grp == group_:
                            if active == None:
                                objs.append(role.user)
                            elif role.user.active == active:
                                objs.append(role.user)
        else:
            if group == []: # ie all
                role_ = self.tables['Role'].selectBy(name=role).getOne()
                app_ = self.tables['App'].selectBy(name=application).getOne()
                roles = self.tables['Roles'].selectBy(application=app_, role=role_)
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if active == None:
                            objs.append(role.user)
                        elif role.user.active == active:
                            objs.append(role.user)
            else:
                role_ = self.tables['Role'].selectBy(name=role).getOne()
                app_ = self.tables['App'].selectBy(name=application).getOne()
                if group == None:
                    group_ = None
                else:
                    group_ = self.tables['Group_'].selectBy(name=group).getOne()
                roles = self.tables['Roles'].selectBy(application=app_, role=role_)
                objs = []
                for role in roles:
                    if role.user not in objs:
                        if role.user.grp == group_:
                            if active == None:
                                objs.append(role.user)
                            elif role.user.active == active:
                                objs.append(role.user)
        users = []
        for obj in objs:
            users.append(obj.user)
        users.sort()
        return tuple(users)

    def _driver_roles(self, username=None, application=None):
        if username == None and application == None:
            roles = []
            objs = self.tables['Role'].select()
            for role in objs:
                roles.append(role.name)
            return tuple(roles)
        if username != None and application != None:
            user = self.tables['User'].selectBy(user=username).getOne()
            app = self.tables['App'].selectBy(name=application).getOne()
            r = []
            for role in self.tables['Roles'].selectBy(application=app, user=user):
                #raise Exception(role, dir(role))
                r.append(role.role.name)
            return tuple(r)
        else:
            if username != None:
            #and application == None:
                objs = self.tables['User'].selectBy(user=username).getOne().roles
                d = {}
                for obj in objs:
                    if d.has_key(obj.application.name):
                        d[obj.application.name].append(obj.role.name)
                    else:
                        d[obj.application.name]=[obj.role.name]
                d1 = {}
                for k,v in d.items():
                    d1[k] = tuple(v)
                if application == None:
                    return d1
                else:
                    return d1[application]
            if application != None:
                app = self.tables['App'].selectBy(application=application).getOne()
                objs = self.tables['Roles'].selectBy(application=app)
                roles = []
                for obj in objs:
                    roles.append(obj.role)
                return tuple(roles)

#
# Remove Objects
#

    def _driver_remove_user(self, username):
        """
        Remove a user and their associated roles.
        
        Remove the user ``username`` unless the username doesn't exist in which case raise an 
        ``authkit.AuthError``.
        
        Remove all roles associated with the user. 
        """
        user = self.tables['User'].selectBy(user=username).getOne()
        for role in user.roles:
            role.destroySelf()
        user.destroySelf()
        
    def _driver_remove_application(self, name, unset_roles): # Changed - can't remove application if it is in use
        """
        Remove the application ``name`` if certain conditions are met
        
        If ``unset_roles`` is False
        and any users have roles associated with the application being removed raise an ``authkit.AuthError``. 
        If ``unset_roles`` is set to ``True`` remove all roles assoicated with the application. 
        
        If ``name`` is ``default`` and ``unset_roles`` is ``True``, remove all roles associated with the default 
        application but DO NOT remove it. If ``unset_roles`` is ``False`` raise an ``authkit.AuthError`` stating
        ``"The default application cannot be removed"``.
        
        If ``name`` is not ``default`` and no error is raised remove the appliaction.
        """
        if unset_roles:
            app = self.tables['App'].selectBy(name=name).getOne(None)
            if app:
                #print repr(app)
                for role in self.tables['Roles'].selectBy(application=app):
                    role.destroySelf()
        else:
            if name == 'default':
                raise AuthError('The default application cannot be removed')
            app = self.tables['App'].selectBy(name=name).getOne(None)
            if app:
                roles = self.tables['Roles'].selectBy(application=app)
                users = ''
                for role in roles:
                    users += ", "+role.user
                if len(users)>0:
                    raise AuthError('The application %s is still in use specifying roles for the following users: %s'%(repr(name), users[2:]))
        app.destroySelf()

    def _driver_remove_role(self, role, unset_roles):
        """
        Remove the ``role`` if certain conditions are met
        
        If the ``role`` doesn't exist raise an ``authkit.AuthError``. If ``unset_roles`` is False
        and any users are currently assinged the role raise an ``authkit.AuthError``. 
        If ``unset_roles`` is set to ``True`` remove all roles assoicated with the application. If an 
        ``authkit.AuthError`` was not raised, remove the role.
        """
        if unset_roles:
            role_ = self.tables['Role'].selectBy(name=role).getOne()
            for role in self.tables['Roles'].selectBy(role=role_):
                role.destroySelf()
        else:
            role_ = self.tables['Role'].selectBy(name=role).getOne()
            roles = self.tables['Roles'].selectBy(name=role_)
  
            users = ''
            for row in roles:
                users += ", "+row.user
            if len(users)>0:
                raise AuthError('The role %s is still in use by the following users: %s'%(repr(role), users[2:]))
        role_.destroySelf()

    def _driver_remove_group(self, group, remove_users=False):
        # Check the roles aren't already in use:
        
        if remove_users:
            group_ = self.tables['Group_'].selectBy(name=group).getOne()
            for user in self.tables['User'].selectBy(grp=group_):
                user.destroySelf()
        else:
            group_ = self.tables['Group_'].selectBy(name=group).getOne()
            users = self.tables['User'].selectBy(grp=group_)
            users_ = ''
            for user in users:
                users_ += ", "+user.user
            if len(users_)>0:
                raise AuthError('The group %s is still in use by the following users: %s'%(repr(group), users_[2:]))
        group_.destroySelf()
    
#
# Object Exists
#

    def _driver_application_exists(self, name):
        """
        Return ``True`` if the application ``name`` exists, ``False`` otherwise. 
        """ 
        if self.tables['App'].selectBy(name=name).getOne(None):
            return True
        return False
            
    def _driver_user_exists(self, username):
        """
        Return ``True`` if the user with the username ``username`` exists, ``False`` otherwise
        """ 
        for x in self.tables['User'].selectBy(user=username):
            return True
        return False
        
    def _driver_role_exists(self, role):
        """
        Return ``True`` if the role ``role`` exists, ``False`` otherwise. 
        """
        if self.tables['Role'].selectBy(name=role).getOne(None):
            return True
        return False

    def _driver_group_exists(self, group):
        """
        Return ``True`` if ``group`` exists or is ``None`` (since no group should always exist), ``False`` otherwise. 
        """
        if group == None:
            return True
        else:
            if self.tables['Group_'].selectBy(name=group).getOne(None):
                return True
            return False

#
# Add Object
#

    def _driver_add_user(self, username, password='', firstname='', surname='', email='', active=True, group=None):
        """
        Add a user
        
        Add a user ``username`` unless the username already exists in which case raise an ``authkit.AuthError``.
        
        Optionally specify a ``password``, ``firstname``, ``surname``, ``email`` and ``group`` for the user and
        set the user's account status with ``active``.
        
        User passwords are already encrypted, if necessary, by the time this method is called so can be treated as 
        strings without needing any modification.
        
        ``password``, ``firstname``, ``surname``, ``email`` can never be ``None`` but can be ``''``. ``group`` can 
        be ``None`` to indicate no group assignment. ``active`` can only be ``True`` or ``False``.
        """
        if group != None:
            # The fact the group exists has already been checked
            
            group_id = self.tables['Group_'].selectBy(name=group).getOne()
        else:
            group_id = None
        new_user = self.tables['User']( 
            user=username, 
            password=password, 
            firstname=firstname, 
            surname=surname, 
            email=email, 
            active=active, 
            grp=group_id,
        )

    def _driver_add_application(self, name): 
        """
        Add an appliation
        
        Add an application ``name``. ``A call to _driver_application_exists()`` will already have been made.
        """
        new_app = self.tables['App'](name=name)
            


    def _driver_add_group(self, group):
        new_role = self.tables['Group_'](name=group)

#
# Roles
#

    def _driver_set_role(self, username, roles, application):
        user = self.tables['User'].selectBy(user=username).getOne().id
        app = self.tables['App'].selectBy(name=application).getOne().id
        for role in roles:
            if not self.role_exists(role):
                raise AuthError("The '%s' role doesn't exist in the database."%role)
            if role in self.roles(username, application):
                raise AuthError('User %s already has the role %s for the application %s'%(repr(username), repr(role), repr(application)))
            else:
                r = self.tables['Role'].selectBy(name=role).getOne().id
                new_role = self.tables['Roles'](role=r, application=app, user=user)

    def _driver_add_role(self, role):
        """
        Adds the role ``role`` to the store unless it already exists in which case an 
        ``authkit.AuthError`` is raised.
        """
        new_role = self.tables['Role'](name=role)

    def _driver_unset_role(self, username, role, application):
        if not self.role_exists(role):
            raise AuthError("The '%s' role doesn't exist in the database."%role)
        if role not in self.roles(username, application):
            raise AuthError('User %s does not have the role %s for the application %s'%(repr(username), repr(role), repr(application)))
        else:
            user = self.tables['User'].selectBy(user=username).getOne()
            app = self.tables['App'].selectBy(name=application).getOne()
            role = self.tables['Role'].selectBy(name=role).getOne()
            for role in self.tables['Roles'].selectBy(role=role, application=app, user=user):
                role.destroySelf()
#
# History Methods
#
    def _driver_history(self, username):
        history = self.tables['User'].selectBy(user=username).getOne().history
        rows = []
        if history:
            for h in history:
                rows.append((h.signed_out, h.signed_in, h.last_accessed))
        def cmp(a, b):
            for x in [0,1,2]:
                if a[x] == None :
                    if b[x] == None:
                        pass
                    else:
                        return -1
                elif b[x] == None:
                    return 1
                elif a[x] > b[x]:
                    return 1
                elif a[x] < b[x]:
                    return -1
                else:
                    pass
            return 0
        rows.sort(cmp)
        return rows

    def _driver_sign_out(self, username):
        user = self.tables['User'].selectBy(user=username).getOne()
        histories = self.tables['History'].selectBy(user=user)
        for history in histories:
            history.signed_out=datetime.datetime(2005,12,12,12).now()
        
    def _driver_sign_in(self, username):
        now = datetime.datetime(2005,12,12,12).now()
        user = self.tables['User'].selectBy(user=username).getOne()
        new_sign_in = self.tables['History'](user=user, signed_in=now, last_accessed=now, signed_out=None)
        
    def _driver_signed_in(self, username):
        if self.tables['History'].selectBy(user=username, signed_out=None).getOne(None):
            return True
        return False

    def _driver_update_accessed(self, username):
        history = self.tables['User'].selectBy(user=username).getOne().history
        if history:#raise Exception(history)
            for h in history:#history = self.tables['History'].selectBy(user=, signed_out=None).getOne()
                if h.last_accessed == None:
                    h.last_accessed = datetime.datetime(2005,12,12,12).now()

#
# User class methods
#
            
    def _driver_user(self, username, property=None): # Changed - removed property
        if self.user_exists(username):
            object = self.tables['User'].selectBy(user=username).getOne()
            
            group = None
            a = object.grp
            if a:
                group = a.name
            
            #group = self.tables['Group_'].get(object.grp)#.getOne().name
            user = {
                'username':object.user,
                'password':object.password,
                'firstname':object.firstname,
                'surname':object.surname,
                'email':object.email,
                'active':object.active,
                'group':group,
                #'levels':self.levels(username), # Changed from level
                'roles':self.roles(username),
            }
            if property:
                if user.has_key(property):
                    return user[property]
                else:
                    raise AuthError('Invalid user property %s'%(repr(property)))
            return user
        else:
            raise AuthError("No such username '%s'."%username)

    def _driver_set_user(self, username, **properties):
        """Private method to set the value of one of 'password', 'firstname', 'surname' and 'email' for a particular user."""
        username = username.lower()
        for property in properties.keys():
            value = properties[property]
            if property in ['password','firstname','surname','email']:
                if self.user_exists(username):
                    setattr(self.tables['User'].selectBy(user=username).getOne(), property, value)
                else:
                    raise AuthError('That user doesn\'t exist.')
            elif property == 'group':
                if self.group_exists(value):
                    group_ = self.tables['Group_'].selectBy(name=value).getOne()
                    self.tables['User'].selectBy(user=username).getOne().grp = group_
                    #setattr(self.tables['User'].selectBy(user=username).getOne(), property, )
                else:
                    raise AuthError('No such group %s'%repr(value))
            elif property == 'active':
                if value in [0,1]:
                    setattr(self.tables['User'].selectBy(user=username).getOne(), property, value)
                else:
                    raise AuthError('active can only br True or False not %s'%repr(value))
            else:
                raise AuthError("You can only set the properties password, firstname, surname, email, active and group")
