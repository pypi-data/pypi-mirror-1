"""Objects representing users, their passwords, roles and groups

The objects defined in this file used in conjunction with authentication,
authorization and permission objects form a complete user management system.

However, there is no requirement to use this user management API at all. If you
define your own authentication checks by specifying your own
``valid_password()`` or ``digest_password()`` methods when setting up the
authentication middleware, and you create your own permissions objects based on
your own requriements then you will have no need for this implementation. It is
simply provided as a useful default implementation for users looking for a
simple, ready made solution that doesn't require any integration. 

The implementation consists of the following:

    ``authkit.authenticate.valid_password()``
        A ``valid_password()`` implementation used by default with the
        ``basic`` or ``form`` authentication methods that checks usernames and
        passwords against those defined in the user management API object.
     
    ``authkit.authenticate.digest_password()``
        A ``digest_password()`` implementation used by default with the
        ``digest`` authentication which produces a digest from the users set up
        in the user management API object.

    ``authkit.permissions.HasAuthKitRole``
        A permission object which checks the signed in user's role from the 
        user management API object.

    ``authkit.permissions.HasAuthKitGroup``
        A permission object which checks the signed in user's group from the 
        user management API object.

    ``authkit.permissions.ValidAuthKitUser``
        A permission object which checks the signed in user is defined in the 
        user management API object.

Of course since the user management API is fairly generic, it is possible to
have different implementations. This module has two implementations both
derived from the base ``Users`` class. They are ``UsersFromString`` and
``UsersFromFile``. By default, ``authkit.authenticate.middleware`` uses
``UsersFromString`` and expects you to specify your users, groups and roles as
a string in the config file in the way described in the main AuthKit manual but
you can also specify you wish to use the alternative implementation to load
your user data from a file.

Of course you are also free to create your own implementation derived from
``Users`` and as long as it keeps the same API, the existing functions and
permissions mentioned earlier will work without modification when using your
user management API object. This means that if your requirements are very
simple you might prefer to create a custom ``Users`` object rather than
integrate AuthKit into your project in the slightly lower level fashion by
defining the ``valid_password()`` and ``digest_password()`` functions and any
necessary permissions.

If you are using the authentication middleware with users, the ``Users`` object
will be available in your code as ``environ[authkit.users]``.  
"""

from authkit.authenticate import AuthKitConfigError

class Users:
    """
    Base class from which all other Users classes should be derived.
    """
    pass

class UsersFromString(Users):
    """
    A ``Users`` class which cbtains user information from a string with lines
    formatted as` ``username1:password1:group role1, role2 etc`` where 
    ``group`` is optional and zero or more roles can exist. 

    One set of user information should be on each line and extra whitespace
    is stripped.
    """
    def __init__(self, data):
        self.usernames, self.passwords, self.roles, self.groups = self.parse(data)
    
    def parse(self, data):
        passwords = {}
        roles = {}
        groups = {}
        counter = 1
        for line in data.split('\n'):
            line = line.strip()
            if not line:
                continue
            role_list = []
            parts = line.split(' ')
            if len(parts) > 1:
                for role in parts[1:]:
                    if role:
                        role_list.append(role.strip().lower())
            group = None
            parts = parts[0].split(':')
            if len(parts) > 1:
                password = parts[1]
                if not password:
                    'Password for %s is empty'%(
                        username,
                    )
                username = parts[0].lower()
                if not username:
                    'Username on line %s is empty'%(
                        counter,
                    )
            if len(parts) == 3:
                group = parts[2].lower()
            if len(parts) < 1 or len(parts) > 3:
                raise AuthKitConfigError(
                    'Syntax error on line %s of authenticate list'%(
                        counter,
                    )
                )
            if passwords.has_key(username):
                raise AuthKitConfigError(
                    'Username %r defined twice in authenticate list %r'%(
                        username,
                        passwords
                    )
                )
            else:
                passwords[username] = password
            if role_list:
                roles[username] = role_list
            if group:
                groups[username] = group
            counter += 1
        usernames = passwords.keys()
        return usernames, passwords, roles, groups

class UsersFromFile(UsersFromString):
    """
    A Users class with the same implementation as ``UsersFromString`` except that
    user information is obtained from a file. The file should contain user information
    in the same format as the string accepted for ``UsersFromString``.
    """
    def __init__(self, filename):
        string = None
        try:
            fp = open(filename, 'r')
            string = filename.read()
        finally:
            fp.close()
        self.usernames, self.passwords, self.roles, self.groups = self.parse(string)

