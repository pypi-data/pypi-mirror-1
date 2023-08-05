#
# Copyright (c) James Gardner <james@jimmyg.org> 2002-2005 All Rights Reserved
# Licensed under LGPL
#

"""Database driver for AuthKit.

Developer Notes:

* User columns are named ``user`` rather than ``username`` to avoid problems with Gadfly
* The Group column is named ``grp`` rather than ``group`` to avoid confusion with SQL ``GROUP BY``
"""

from authkit import AuthError, AuthStore
import datetime

try:
    True
    False
except NameError:
    True = 1==1
    False = 0==1

class DatabaseAuthStore(AuthStore):
    """
    An auth store which makes use of the PythonWeb.org ``database`` module to store auth information in 
    an SQL database.
    
    This driver is know to work with pysqlite 1.1.6 and MySQLdb 1.0.
    
    ``DatabaseAuthStore`` is used as follows::
    
        import database
        connection = database.connect(dsn="sqlite:///test.db")
        cursor = connection.cursor()
        auth = DatabaseAuthStore(cursor=connection.cursor())
        
    Do whatever you want with the newly created ``auth`` object then save changes::
        
        connection.commit()
    """

    def __init__(self, cursor, table_prepend='AuthKit_', **auth_store_params):
        self.cursor = cursor
        self._table_prepend = table_prepend
        AuthStore.__init__(self, **auth_store_params)

    #
    # Environment Methods
    #
    
    def _driver_create_store(self):
        """
        Destroy any existing store and create the auth store.
        
        If any errors are generated when creating the store an ``authkit.AuthError`` is raised.
        """
        errors = []
        if not self.cursor.tableExists(self._table_prepend+'User'):
            self.cursor.create(
                table=self._table_prepend+'User',
                columns=[    
                    ('user',     'String' ),
                    ('password', 'String'),# required=True, default=''),
                    ('firstname','String'),#required=True, default=''),
                    ('surname',  'String'),# required=True, default=''),
                    ('email',    'String'),# required=True, default=''),
                    ('active',   'Bool'),#  required=True, default=1),
                    ('grp',      'String' ),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'User'+"' table already exists.")
        if not self.cursor.tableExists(self._table_prepend+'App'):
            self.cursor.create(
                table=self._table_prepend+'App',
                columns=[  
                    ('name',     'String' ),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'App'+"' table already exists.")
        if not self.cursor.tableExists(self._table_prepend+'Group'):
            self.cursor.create(
                table=self._table_prepend+'Group',
                columns=[    
                    ('name',     'String' ),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'Group'+"' table already exists.")
        if not self.cursor.tableExists(self._table_prepend+'Role'):
            self.cursor.create(
                table=self._table_prepend+'Role',
                columns=[    
                    ('name',     'String' ),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'Role'+"' table already exists.")
        if not self.cursor.tableExists(self._table_prepend+'Roles'):
            self.cursor.create(
                table=self._table_prepend+'Roles',
                columns=[  
                    ('user',     'String'),
                    ('application',      'String'),
                    ('role',     'String'),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'Roles'+"' table already exists.")
        if not self.cursor.tableExists(self._table_prepend+'History'):
            self.cursor.create(
                table=self._table_prepend+'History',
                columns=[  
                    ('user',          'String'),
                    ('signed_in',     'DateTime'),
                    ('last_accessed', 'DateTime'),
                    ('signed_out',    'DateTime'),
                ]
            )
        else:
            errors.append("The '"+self._table_prepend+'History'+"' table already exists.")
        if errors:
            raise AuthError(', '.join(errors))

    def _driver_remove_store(self):
        """
        Remove the auth store, destroying any data it contains. If there are no problems, ``[]`` is returned.
        
        If any errors occurs preventing the store from being removed an ``authkit.AuthError`` is raised. 
        If the store doesn't exist or only partially exists, any warnings are returned as a list of strings.
        """
        errors = []
        for table in [
            'User',
            'App', 
            'Group', 
            'Role', 
            'Roles'
            'History'
        ]:
            try:
                self.cursor.drop(self._table_prepend+table)
            except:
                errors.append("The "+self._table_prepend+table+" table may not exist. Error: %s"%str(sys.exc_info()[1]))
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
        if  self.cursor.tableExists(self._table_prepend+'User') and \
            self.cursor.tableExists(self._table_prepend+'App') and \
            self.cursor.tableExists(self._table_prepend+'Group') and \
            self.cursor.tableExists(self._table_prepend+'Role') and \
            self.cursor.tableExists(self._table_prepend+'History') and \
            self.cursor.tableExists(self._table_prepend+'Roles'):
            return True
        else:
            return False

    #
    # Applications
    #
    
    def _driver_applications(self):
        """
        Return a list of applications in the store, including the ``default`` application.
        """
        rows = self.cursor.select(
            'name', 
            '%sApp'%self._table_prepend,
            fetch=True,
            format='tuple',
            convert=True,
        )
        apps = []
        if rows:
            for row in rows:
                apps.append(row[0])
        return tuple(apps)
            
    def _driver_application_exists(self, name):
        """
        Return ``True`` if the application ``name`` exists, ``False`` otherwise. 
        """ 
        rows = self.cursor.select(
            'name',
            '%sApp'%self._table_prepend, 
            where="name='"+name+"'", 
            fetch=True,
            format='tuple',
            convert=True,
        )
        if rows:
            return True
        return False
            
    def _driver_add_application(self, name): 
        """
        Add an appliation
        
        Add an application ``name``. ``A call to _driver_application_exists()`` will already have been made.
        """
        self.cursor.insert('%sApp'%self._table_prepend, ['name'], [name])
            
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
            self.cursor.delete('%sRoles'%self._table_prepend,where="application='"+name+"'")
        else:
            if name == 'default':
                raise AuthError('The default application cannot be removed')
            rows = self.cursor.select(
                'user',
                '%sRoles'%self._table_prepend, 
                where="application='"+name+"'", 
                fetch=True,
                format='tuple',
                convert=True,
            )
            if rows:
                users = ''
                for row in rows:
                    users += ", "+row[0]
                raise AuthError('The application %s is still in use specifying roles for the following users: %s'%(repr(name), users[2:]))
        self.cursor.delete('%sApp'%self._table_prepend, where="name='"+name+"'")

    #
    # Users
    #

    def _driver_user_exists(self, username):
        """
        Return ``True`` if the user with the username ``username`` exists, ``False`` otherwise. The username is lowercase.
        """ 
        rows = self.cursor.select(
            'user',
            '%sUser'%self._table_prepend, 
            where="user='"+username+"'", 
            fetch=True,
            format='tuple',
            convert=True,
        )
        if rows:
            return True
        return False
        
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
        
        User is guaranteed not to already exist.
        """
        self.cursor.insert(
            '%sUser'%self._table_prepend,
            ('user', 'password', 'firstname', 'surname', 'email', 'active', 'grp'),
            (username, password, firstname, surname, email, active, group),
        )

    def _driver_remove_user(self, username):
        """
        Remove a user and their associated roles.
        
        Remove the user ``username`` unless the username doesn't exist in which case raise an 
        ``authkit.AuthError``.
        
        Remove all roles associated with the user. 
        """
        if self.user_exists(username):
            self.cursor.delete('%sUser'%self._table_prepend,where="user='"+username+"'")
        else:
            raise AuthError("The user '%s' doesn't exist."%(username))
        self.cursor.delete('%sRoles'%self._table_prepend,where="user='"+username+"'")

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
        """
        rows = []
        if (application==None and role!= None) or (application != None and role == None):
            raise AuthError('You must specify both role and application or neither of them')
        if group != [] and group!=None and not self.group_exists(group):
            raise AuthError('No such group %s'%repr(group))
        if application == None:
            if group == []: # ie all
                if active == None:
                    rows = self.cursor.select(
                        'user', 
                        tables='%sUser'%self._table_prepend,
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
                else:
                    rows = self.cursor.select(
                        'user', 
                        tables='%sUser'%self._table_prepend,
                        where="active=? ",
                        values = [active],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
            else:
                if active == None:
                    rows = self.cursor.select(
                        'user', 
                        tables='%sUser'%self._table_prepend,
                        where="grp=?",
                        values = [group],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
                else:
                    rows = self.cursor.select(
                        'user', 
                        tables='%sUser'%self._table_prepend,
                        where="grp= ? and active= ? ",
                        values = [group, active],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
        else:
            if group == []: # ie all
                if active == None:
                    rows = self.cursor.select(
                        'user',
                        tables=['%sRoles'%self._table_prepend],
                        where="application=? and role=? ",
                        values = [application, role],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
                else:
                    rows = self.cursor.select(
                        ('%sUser'%self._table_prepend+'.user'),
                        tables=['%sUser'%self._table_prepend, '%sRoles'%self._table_prepend],
                        where="%sUser.active=? and %sRoles.application=? and %sRoles.role=? and %sUser.user=%sRoles.user "%(
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend,
                            self._table_prepend,
                            self._table_prepend,
                        ),
                        values = [active, application, role],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
            else:
                if active == None:
                    rows = self.cursor.select(
                        ('%sUser'%self._table_prepend+'.user'),
                        tables=['%sUser'%self._table_prepend, '%sRoles'%self._table_prepend],
                        where="%sUser.grp=? and %sUser.user=%sRoles.user and %sRoles.application=? and %sRoles.role=?"%(
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend
                        ),
                        values = [group, application, role],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )
                else:
                    rows = self.cursor.select(
                        ('%sUser'%self._table_prepend+'.user'),
                        tables=['%sUser'%self._table_prepend, '%sRoles'%self._table_prepend],
                        where="%sUser.grp=? and %sUser.active=? and %sRoles.application=? and %sRoles.role=? and %sUser.user=%sRoles.user"%(
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend, 
                            self._table_prepend
                        ),
                        values = [group, active, application, role],
                        fetch=True,
                        format='tuple',
                        convert=True,
                    )

        users = []
        for row in rows:
            users.append(row[0])
        return tuple(users)

    #
    # Roles
    #

    def _driver_add_role(self, role):
        """
        Adds the role ``role`` to the store unless it already exists in which case an 
        ``authkit.AuthError`` is raised.
        """
        self.cursor.insert('%sRole'%self._table_prepend, ['name'], [role])

    def _driver_role_exists(self, role):
        """
        Return ``True`` if the role ``role`` exists, ``False`` otherwise. 
        """
        rows = self.cursor.select(
            'name',
            '%sRole'%self._table_prepend, 
            where="name='"+role+"'", 
            fetch=True,
            format='tuple',
            convert=True,
        )
        if rows:
            return True
        else:
            return False

    def _driver_remove_role(self, role, unset_roles):
        """
        Remove the ``role`` if certain conditions are met
        
        If the ``role`` doesn't exist raise an ``authkit.AuthError``. If ``unset_roles`` is False
        and any users are currently assinged the role raise an ``authkit.AuthError``. 
        If ``unset_roles`` is set to ``True`` remove all roles assoicated with the application. If an 
        ``authkit.AuthError`` was not raised, remove the role.
        """
    
        # Check the roles aren't already in use:
        if unset_roles:
            self.cursor.delete(
                table='%sRoles'%self._table_prepend, 
                where="role='"+role+"'", 
            )
        else:
            rows = self.cursor.select(
                'user',
                '%sRoles'%self._table_prepend, 
                where="role='"+role+"'", 
                fetch=True,
                format='tuple',
                convert=True,
            )
            if rows:
                users = ''
                for row in rows:
                    users += ", "+row[0]
                raise AuthError('The role %s is still in use by the following users: %s'%(repr(role), users[2:]))
        self.cursor.delete('%sRole'%self._table_prepend,where="name='"+role+"'")

    def _driver_roles(self, username=None, application=None):
        if username != None and application != None:
            rows = self.cursor.select(
                ['role', 'application'],
                '%sRoles'%self._table_prepend, 
                where = "application='"+application+"' and user='"+username+"'",
                fetch=True,
                format='tuple',
                convert=True,
            )
            roles = []
            for row in rows:
                roles.append(row[0])
            return tuple(roles)
        else:
            if username != None and application == None:
                rows = self.cursor.select(
                    ['role','application'],
                    '%sRoles'%self._table_prepend, 
                    where = "user='"+username+"'",
                    fetch=True,
                    format='tuple',
                    convert=True,
                )
                d = {}
                for row in rows:
                    d[row[1]] = row[0]
                return d
            else:
                rows = self.cursor.select(
                    'name',
                    '%sRole'%self._table_prepend, 
                    fetch=True,
                    format='tuple',
                    convert=True,
                )
                roles = []
                for row in rows:
                    roles.append(row[0])
                return tuple(roles)

    def _driver_set_role(self, username, role, application):
        roles = role
        if not (isinstance(role, tuple) or isinstance(role, list)):
            roles = [role]
        for role in roles:
            if not self.role_exists(role):
                raise AuthError("The '%s' role doesn't exist in the database."%role)
            if role in self.roles(username, application):
                raise AuthError('User %s already has the role %s for the application %s'%(repr(username), repr(role), repr(application)))
            else:
                self.cursor.insert('%sRoles'%self._table_prepend, ['role','application','user'], [role, application, username])

    def _driver_unset_role(self, username, role, application):
        if not self.role_exists(role):
            raise AuthError("The '%s' role doesn't exist in the database."%role)
        if role not in self.roles(username, application):
            raise AuthError('User %s does not have the role %s for the application %s'%(repr(username), repr(role), repr(application)))
        else:
            self.cursor.delete('%sRoles'%self._table_prepend, where = "application='"+application+"' and user='"+username+"' and role='"+role+"'",)

    #
    # Groups
    #

    def _driver_group_exists(self, group):
        """
        Return ``True`` if ``group`` exists or is ``None`` (since no group should always exist), ``False`` otherwise. 
        """
        if group == None:
            return True
        else:
            rows = self.cursor.select(
                'name',
                '%sGroup'%self._table_prepend, 
                where="name='"+group+"'", 
                fetch=True,
                format='tuple',
                convert=True,
            )
            if rows:
                return True
            else:
                return False
        
    def _driver_add_group(self, group):
        if self.group_exists(group):
            raise AuthError("The '%s' group already exists."%group)
        else:
            self.cursor.insert('%sGroup'%self._table_prepend, ['name'], [group])

    def _driver_remove_group(self, group, force=0):

        # Check the roles aren't already in use:
        if force:
            self.cursor.update(
                '%sUser'%self._table_prepend, 
                ['grp'],[None, group],
                where="grp=?",
            )
        else:
            rows = self.cursor.select(
                'user',
                '%sUser'%self._table_prepend, 
                where="grp=?", 

                values = [group],
                fetch=True,
                format='tuple',
                convert=True,
            )
            users = ''
            for row in rows:
                users += ", "+row[0]
            raise AuthError('The group %s is still in use by the following users: %s'%(repr(group), users[2:]))
        self.cursor.delete('%sGroup'%self._table_prepend, where="name='"+group+"'")

    def _driver_groups(self):
        rows = self.cursor.select(
            'name',
            '%sGroup'%self._table_prepend, 
            fetch=True,
            format='tuple',
            convert=True,
        )
        groups = []
        for row in rows:
            groups.append(row[0])
        return tuple(groups)

    #
    # History Methods
    #
    def _driver_history(self, username):
        where = "user='%s'"%username
        #for username in usernames:
        #    where += "user='%s' or "%username
        rows = self.cursor.select(
            ['signed_in','last_accessed','signed_out'],
            '%sHistory'%self._table_prepend, 
            where=where,
            fetch=True,
            format='tuple',
            convert=True,
        )
        return rows

    def _driver_sign_out(self, username):
        self.cursor.update(
            table='%sHistory'%self._table_prepend, 
            columns=['signed_out'],
            values = [datetime.datetime(2005,12,12,12).now()],
            where="user='%s'"%username,
        )
        #raise Exception(rows)
        
    def _driver_sign_in(self, username):
        now = datetime.datetime(2005,12,12,12).now()
        self.cursor.insert(
            table='%sHistory'%self._table_prepend, 
            columns=['user', 'signed_in', 'last_accessed'],
            values = [username, now, now],
        )
        
    def _driver_signed_in(self, username):
        rows = self.cursor.select(
            'user',
            '%sHistory'%self._table_prepend, 
            where="user='%s' and signed_out IS NULL"%username,
            fetch=True,
            format='tuple',
            convert=True,
            order = 'signed_in'
        )
        if len(rows) > 0:
            return 1
        return 0

    def _driver_update_accessed(self, username):
        self.cursor.update(
            '%sHistory'%self._table_prepend, 
            ('last_accessed',), 
            (datetime.datetime(2005,12,12,12).now(),), 
            where="%s='%s' and signed_out is NULL"%('user',username)
        )
                
        #self.tables['History'].selectBy(user=username, signed_out=None)[0].last_accessed = 


    #
    # User class methods
    #
            
    def _driver_user(self, username, property=None): # Changed - removed property
        if self.user_exists(username):
            rows = self.cursor.select(
                ('user','password','firstname','surname','email','active','grp'), 
                '%sUser'%self._table_prepend, 
                where="user='%s'"%username, 
                fetch=True,
                format='dict',
                convert=True,
            )
            object = rows[0]
            user = {
                'username':object['user'],
                'password':object['password'],
                'firstname':object['firstname'],
                'surname':object['surname'],
                'email':object['email'],
                'active':object['active'],
                'group':object['grp'],
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
                    self.cursor.update('%sUser'%self._table_prepend, (property,), (value,), where="%s='%s'"%('user',username))
                else:
                    raise AuthError('That user doesn\'t exist.')
            elif property == 'group':
                if self.group_exists(value):
    
                    self.cursor.update('%sUser'%self._table_prepend, ('grp',), (value,), where="%s='%s'"%('user',username))
                else:
                    raise AuthError('No such group %s'%repr(value))
            elif property == 'active':
                if value in [0,1]:
                    self.cursor.update('%sUser'%self._table_prepend, (property,), (value,), where="%s='%s'"%('user',username))
                else:
                    raise AuthError('active can only br True or False not %s'%repr(value))
            else:
                raise AuthError("You can only set the properties password, firstname, surname, email, active and group")
