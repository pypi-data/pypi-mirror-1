"""Authentication middleware

This module provides one piece of middleware named 
``authkit.authenticate.middleware`` which is used to intercept responses with
a specified status code, present a user with a means of authenticating 
themselves and handle the sign in process.

Each of the authentication methods supported by the middleware is described in
detail in the main AuthKit manual. The methods include:

* HTTP Basic (``basic``)
* HTTP Digest (``digest``)
* OpenID Passurl (``passurl``)
* Form and Cookie (``form``)
* Forward (``forward``)

The authenticate middleware can be configured directly or by means of a Paste
deploy config file as used by Pylons. It can be used directly like this:

.. code-block:: Python

    from authkit.authenticate import middleware, test_app
    from paste.httpserver import serve

    import sys
    app = middleware(
        test_app,
        enable = True,
        method = 'passurl',
        cookie_secret='some_secret',
    )
    
    serve(app, host='0.0.0.0', port=8000)

"""

import types
import warnings
import logging

from paste.util.import_string import eval_import
from multi import MultiHandler, ChangeTo401, status_checker

#
# Setting up logging
#

log = logging.getLogger('authkit.authenticate')
    
#
# Exceptions
#

class AuthKitConfigError(Exception): 
    """
    Raised when there is a problem with the
    configuration options chosen for the authenticate middleware
    """
    pass

no_authkit_users_in_environ = AuthKitConfigError(
    'No authkit.users object exists in the environment. You may have '
    'forgotton to specify a Users object or are using the the default '
    'valid_password() method in the authenticate middleware when you '
    'may have meant to specify your own.'
)

#
# Default values
#

_allowed_options = [
    'method',        
    'catch',         
    'exclude',
    'enable',
    
    'form_template_obj',     
    'form_template_file',       
    'form_template',            
    'realm',    
    
    'users_object',
    'users_setup',
    'users_valid',
    'users_digest',

    'passurl_path_process',
    'passurl_urltouser',
    'passurl_path_verify',
    'passurl_path_signedin',
    'passurl_baseurl',
    'passurl_template',
    'passurl_template_obj',
    'passurl_template_file',
    'passurl_session_middleware',
    'passurl_session_key',
    'passurl_session_secret',
    'passurl_store_config',
    'passurl_store_type',
    
    'cookie_secret',           
    'cookie_name',             
    'cookie_secure',            
    'cookie_includeip',         
    'cookie_signout',      
    'cookie_params',
    'cookie_enforce',
    'signin',
]

#
# Useful functions
#

def _get_value(dictionary, option, prefix, allowed_values=[], **p):
    """
    Returns the value ``dictionary[option]`` checking it is one of
    ``allowed_values``
    """
    if not dictionary.has_key(option):
        if p.has_key('default'):
            return p['default']
        else:
            raise AuthKitConfigError(
                "The required option %r was not specified"%_app2key(option, prefix)
            )
    else:
        result = dictionary[option]
        if allowed_values and result not in allowed_values:
            if p.has_key('default'):
                return p['default']
            else:
                raise AuthKitConfigError(
                    "The option %r takes one of the values %r, not %r"%(
                        _app2key(option, prefix),
                        allowed_values,
                        result,
                    )    
                )
        return result

def _convert_config(app_conf, prefix):
    """
    Return the ``app_conf`` dictionary keys in the form they would have been
    entered if the middleware had been setup directly in Python code
    """
    authkit_options = {}
    for key, value in app_conf.items():
        if key[:len(prefix)].lower() == prefix:
            authkit_options[key[len(prefix):].replace('.','_')] = value
    return authkit_options

def _app2key(key, prefix):
    """
    Return the name of the key as it would have specified in the config file
    """
    return prefix+key.replace('_','.')

def _get_one_option_name(final, options, prefix, raise_on_no_match=True):
    """
    Check that the ``final`` dictionary only contains one of the keys 
    specified in ``options``. If ``raise_on_no_match`` is ``True`` an 
    ``AuthKitConfigError`` is raised if none of the options are 
    present.
    """
    found = None
    for option in options:
        if final.has_key(option):
            if option != None:
                found = option
            else:
                raise AuthKitConfigError(
                    'You cannot specify both %r and %r'%(
                        _app2key(found, prefix),
                        _app2key(option, prefix),
                    )
                )
    if found:
        return found
    elif raise_on_no_match:
        raise AuthKitConfigError(
            'Your AuthKit configuration reqiuires one of these options to be '
            'set: %s'%', '.join([_app2key(x, prefix) for x in options])
        )
    return None

def valid_password(environ, username, password): 
    """ 
    A function which can be used with the ``basic`` and ``form`` authentication
    methods to validate a username and passowrd.

    This implementation is used by default if no other method is specified. It
    checks the for an ``authkit.users`` object present in the ``environ``
    dictionary under the ``authkit.users`` key and uses the information there
    to validate the username and password.

    In this implementation usernames are case insensitive and passwords are
    case sensitive. The function returns ``True`` if the user ``username`` has
    the password specified by ``password`` and returns ``False`` if the user
    doesn't exist or the password is incorrect.

    If you create and specify your own ``authkit.users`` object with the same
    API, this method will also work correctly with your custom solution. See
    the AuthKit manual for information on the user management api, how to
    specify a different ``authkit.users`` object (say to read user information
    from a file rather than have it specified directly) and for information on
    how to create your own ``Users`` objects.
    """
    
    if not environ.has_key('authkit.users'):
        raise no_authkit_users_in_environ
    users = environ['authkit.users']
    if users.passwords.has_key(username.lower()) and users.passwords[username.lower()] == password:
        return True
    return False

def digest_password(environ, realm, username):
    """
    This is similar to ``valid_password()`` but is used with the ``digest``
    authentication method and rather than checking a username and password and
    returning ``True`` or ``False`` it takes the realm and username as input,
    looks up the correct password and and returns a digest by calling the
    ``authkit.authenticate.digest.digest_password()`` function with the
    parameters ``realm``, ``username`` and ``password`` respectively. The
    digest returned is then compared with the one submitted by the browser.

    As with ``valid_password()`` this method is designed to work with the user
    management API so you can use it with ``authkit.users`` objects or your own
    custom ``Users`` objects. Alternatively you can specify your own function
    which can lookup the password in whichever way you prefer, perhaps from a
    database or LDAP connection.
    
    Only required if you intend to use HTTP digest authentication.
    """
    #import authkit.authenticate.digest
    if not environ.has_key('authkit.users'):
        raise no_authkit_users_in_environ
    users = environ['authkit.users']
    if users.passwords.has_key(username.lower()):
        password = users.passwords[username.lower()]
        return digest.digest_password(realm, username, password)
    # After speaking to Clark Evans who wrote the origianl code, this is the correct thing:
    return None

def load_cookie_middleware(app, final, prefix):
    """
    Various AuthKit authenticate mathods such as ``form`` and ``passurl`` use a
    cookie. Their cookie support is based on the
    ``authkit.authenticate.auth_tkt`` middleware.  This utility function reads
    the cookie config options and returns the correctly configured cookie
    middleware automatically, reducing duplication in the code.
    """
    from paste.deploy.converters import asbool
    from authkit.authenticate.auth_tkt import AuthKitCookieMiddleware
    params = {
        'secret':_get_value(final, 'cookie_secret', prefix), 
    }
    for param in [
        ['cookie_name','cookie_name'], 
        ['cookie_includeip', 'include_ip'],
        ['cookie_signout', 'logout_path'],
        ['cookie_enforce', 'cookie_enforce'],
    ]:
        if param[0] in final:
            params[param[1]] = final[param[0]]
    cookie_params = {}
    if final.has_key('cookie_params'):
        data = _get_value(final, 'cookie_params', prefix)
        if isinstance(data, str):
            lines = data.replace('\r\n','\n').replace('\r','\n').split('\n')
            for line in lines:
                if line.strip():
                    parts = line.strip().split(':')
                    name = parts[0].strip().lower()
                    if name in [
                        'expires',  
                        'path', 
                        'comment', 
                        'domain',
                        'max-age',
                        'secure',
                        'version',
                    ]:
                        cookie_params[name] = ':'.join(parts[1:]).strip()
                    else:
                        raise AuthKitConfigError('Invalid cookie parameter %r'%name)
        elif isinstance(data, dict):
            cookie_params = data.copy()
        else:
            raise AuthKitConfigError("Expected a string or dictionary for authkit.cookie_params")
    app = AuthKitCookieMiddleware(app, cookie_params=cookie_params, **params)
    return app

def get_authenticate_function(app, final, prefix, method):
    """
    Sets up the users object, adds the middleware to add the users object
    to the environ and then returns authenticate methods to check a password
    and a digest.
    """
    setup = _get_one_option_name(
        final, 
        ['users_setup', 'users_digest', 'users_valid'],
        prefix,
    )
    users_object = 'authkit.users.UsersFromString'
    if final.has_key('users_object'):
        users_object = final['users_object']
    users_method = 'direct'
    if final.has_key('users_setup'):
        users_method = 'setup'

    valid = None
    digest = None
    
    if users_method == 'setup':
        # Get the users in a standard format that can be added to the environment 
        # and used with the default valid and digest methods below
        parse_users_setup_obj = eval_import(users_object)
        users = parse_users_setup_obj(final['users_setup'])
        app = AddToEnviron(app, 'authkit.users', users)
        if valid == None:
            valid = valid_password
        if digest == None:
            digest = digest_password
    else:
        # Use the methods directly or load them if they are specified as strings
        if method not in ['digest'] and valid == None:
            func = _get_value(final, 'users_valid', prefix)
            if isinstance(func, str):
                valid = eval_import(func)
            else:
                valid = func
        if method == 'digest' and digest == None:
            func = _get_value(final, 'users_digest', prefix)
            if isinstance(func, str):
                digest = eval_import(func)
            else:
                digest = func
    if valid is None and digest is None:
        raise Exception("No valid() method or digest() method found")
    return app, valid, digest
    
def get_template(final, template, base_part, prefix):
    """
    Another utility method to reduce code duplication. This function parses a
    template from one of the available template options:

    ``template``
        The template as a string
        
    ``template_file``
        A file containing the template

    ``template_obj``
        A paste eval_import string or callable which returns a string
    
    ``base_part`` is added to the option name before the option is looked 
    for. This means the code can be used to load templates for various different
    authentication methods with different config options names.
    """
    template_mode = _get_one_option_name(
        final, 
        [
            base_part+'template',
            base_part+'template_file',
            base_part+'template_obj',
        ],
        prefix,
        False,
    )
    if template_mode == base_part+'template_file':
        data = ''
        try:
            fp = open(final[base_part+'template_file'], 'r')
            data = fp.read()
        finally:
            fp.close()
        if not data:
            raise AuthKitConfigError(
                'No data in form template file %s'%(
                    final[base_part+'template_file']
                )
            )
        template = data
    elif template_mode == base_part+'template_obj':
        data = eval_import(final[base_part+'template_obj'])
        if not isinstance(data, (str,unicode)):
            data = data()
        if not data:
            raise AuthKitConfigError(
                'No template data in object %s'%(
                    final[base_part+'template_obj']
                )
            )
        template=data
    elif template_mode == base_part+'template':
        template = _get_value(final, base_part+'template', prefix)
    return template
    
#
# Main middleware creator 
#

class AddToEnviron:
    """
    Simple middleware which adds a key to the ``environ`` dictionary.
    
    Used to add the ``authkit.users`` key to the environ when this is
    appropriate.
    """
    def __init__(self, app, key, object):
        self.app = app
        self.key = key
        self.object = object
        
    def __call__(self, environ, start_response):
        environ[self.key] = self.object
        return self.app(environ, start_response)

def middleware(
    app,
    config_paste = None,
    config_file = None,
    prefix='authkit.',
    custom_methods=None,
    **options
):   
    """
    This function sets up the AuthKit authenticate middleware and its use and options
    are described in detail in the AuthKit manual.
   
    The function takes the following arguments and returns a WSGI application 
    wrapped in the appropriate AuthKit authentication middleware based on the options specified:

    ``app``
        The WSGI application the authenticate middleware should wrap

    ``config_paste``
        A paste deploy ``app_conf`` dictionary to be used to setup the middleware

    ``config_file``
        The path to a config file in the paste deploy format to be used to setup
        the middleware

    ``prefix``
        The prefix which all authkit related options in the config file will
        have prefixed to their names. This defaults to ``authkit.`` and
        shouldn't normally need overriding.

    ``**options``
        Any AuthKit options which are setup directly in Python code. If specified, 
        these options will override any options specifed in a config file.

    Only one of ``config_paste`` and ``config_file`` can be specified. All
    option names specified in the config file will have their prefix removed
    and any ``.`` characters replaced by ``_`` before the options specified by
    ``options`` are merged in. This means that the the option
    ``authkit.cookie.name`` specified in a config file sets the same options as
    ``cookie_name`` specified directly as an option.

    A full list of the options available is specified in the ``_allowed_options`` 
    variable in the source code.
    """

    #
    # Check custom_method names
    #

    if custom_methods:
        for custom_method in custom_methods.keys():
            if custom_method in ['form','forward','basic','digest','passurl']:
                raise Exception(
                    (
                        'The custom method name %r is already used by the '
                        'authkit built-in method. Please choose a '
                        'different name.'
                    ) % custom_method
                )

    #
    # Configure the config files
    #

    if config_file and config_paste:
        raise AuthKitConfigError(
            'Please specify a conf_paste dictionary or a config_filename '
            'but not both'
        )
    if config_file:
        data = ''
        try:
            fp = open(config_file, 'rb')
            data = fp.read()
        finally:
            fp.close()
        config = paste.parse(data)
    elif config_paste:
        if isinstance(config_paste, dict):
            config = config_paste
        else:
            raise AuthKitConfigError(
                "Expected config_paste to be the app_conf dictionary from "
                "paste.deploy.CONFIG['app_conf']"
            )
    else:
        config={}
    
    #
    # Merge config file and options
    #

    final = {}
    for key, value in _convert_config(config, prefix).items():
        if key not in _allowed_options:
            raise AuthKitConfigError(
                'Option key %r specified in config file is not a valid '
                'authkit option'%_app2key(key, prefix))
        if config.has_key(key) and options.has_key(key):
            warnings.warn(
                'Key %s with value %r set in the config file is being ' + \
                'replaced with value %r set in the application'%(
                    key,
                    config[key],
                    options[key]
                )   
            )
        final[key] = value

    method = _get_value(options,'method', prefix)
    
    if custom_methods and method in custom_methods.keys():
        for key, value in options.items():
            final[key] = value
        # Call the make_middleware() function for this method
        app = custom_methods[method](
            app, 
            auth_conf=final, 
            prefix=prefix, 
            app_conf=config
        )
        return app

    # Otherwise we are using one of the standard AuthKit methods

    for key, value in options.items():
        if key not in _allowed_options:
            raise Exception('Parameter %r is not a valid authkit option'%key)
        final[key] = value

    #
    # Create the middleware, checking options as we go
    #
    
    # Check to see if middleware is disabled
    if not options and not final.has_key('enable'):
        warnings.warn(
            "AuthKit middleware has been disabled because authkit.enable "
            "has not been set to 'true'"
        )
        return app
    elif final.has_key('enable') and final['enable'] in [False,'false',0,'0']:
        return app
    elif final.has_key('enable') and final['enable'] not in \
        [True,'true',1,'1']:
        raise AuthKitConfigError(
            'Unrecognised option %r for authkit.enable'%final['enable']
        )    

    # Status Checking/Changing Middleware
    catch = [str(x).strip() for x in final.get('catch','').split(',')]
    exclude = [str(x).strip() for x in final.get('exclude','').split(',')]
    # XXX Could check catch and exclude values are valid here
    if catch or exclude:
        app = ChangeTo401(app, catch=catch, exclude=exclude)

    # Sign in method
    methods = ['form','forward','basic','digest','passurl']
    if custom_methods:
        for custom_method in custom_methods.keys():
            methods.append(custom_method)

    if method not in ['forward','passurl']:  
        app, valid, digest = get_authenticate_function(app, final, prefix, method)
    # define realm
    if method in ['basic','digest']:
        if not final.has_key('realm'):
            final['realm'] = 'AuthKit'

    # Set up the correct middleware
    if method == 'basic':
        from authkit.authenticate.basic import middleware
        app = MultiHandler(app)
        app.add_method(
            'basic', 
            middleware, 
            final['realm'], 
            valid
        )
        app.add_checker('basic', status_checker)
        return app
    elif method == 'digest':
        from authkit.authenticate.digest import middleware
        app = MultiHandler(app)
        app.add_method(
            'digest', 
            middleware, 
            final['realm'], 
            digest
        )
        app.add_checker('digest', status_checker)
        return app
    elif method == 'form':
        from authkit.authenticate.form import Form, template
        template = get_template(final, template, 'form_', prefix)
        if final.has_key('cookie_signout') and not \
            final['cookie_signout'].startswith('/'):
            raise AuthKitConfigError(
                "The cookie signout path should start with a '/' character"
            )
        app = MultiHandler(app)
        app.add_method('form', Form, authfunc=valid, template=template)
        app.add_checker('form', status_checker)
        app = load_cookie_middleware(app, final, prefix)
        return app
    elif method == 'forward':
        from authkit.authenticate.forward import Redirect, MyRecursive, RecursiveMiddleware
        app = MultiHandler(app)
        app.add_method(
            'forward', 
            Redirect,  
            _get_value(final, 'signin', prefix)
        )
        app.add_checker('forward', status_checker)
        app = MyRecursive(RecursiveMiddleware(app))
        app = load_cookie_middleware(app, final, prefix)
        return app
    elif method=='passurl':
        # Note, the session middleware should already be setup by now
        # if we are not using beaker
        from authkit.authenticate.passurl import PassURLSignIn, AuthOpenIDHandler, template
        template = get_template(final, template, 'passurl_', prefix)
        app = MultiHandler(app)
        app.add_method(
            'passurl', 
            PassURLSignIn,  
            template, 
            path_verify=_get_value(final, 'passurl_path_verify', prefix, default='/verify'),
            baseurl=_get_value(final, 'passurl_baseurl', prefix, default='')
        )
        app.add_checker('passurl', status_checker)
        urltouser = _get_value(final, 'passurl_urltouser', prefix, default=None)
        if isinstance(urltouser, str):
            urltouser = eval_import(urltouser)
        app = AuthOpenIDHandler(
            app,
            store_type=_get_value(final, 'passurl_store_type', prefix), 
            store_config = _get_value(final, 'passurl_store_config', prefix),
            baseurl=_get_value(final, 'passurl_baseurl', prefix, default=''),
            path_signedin=_get_value(final, 'passurl_path_signedin', prefix),
            path_process=_get_value(final, 'passurl_path_process', prefix, default='/process'),
            template = template,
            urltouser = urltouser
        )
        session_middleware = 'beaker.session'
        session_secret = 'asdasd'
        session_key = 'authkit_passurl'
        if session_middleware == 'beaker.session':
            if not session_secret:
                raise AuthKitConfigError('No session_secret set')
            from beaker.session import SessionMiddleware
            app = SessionMiddleware(app, key=session_key, secret=session_secret)
            
        app = load_cookie_middleware(app, final, prefix)
        return app
    else:
        raise NotImplementedError('No %r method has been implemented'%method)
            
def test_app(environ, start_response):
    """
    A sample WSGI application that returns a 401 status code when the path 
    ``/private`` is entered, triggering the authenticate middleware to 
    prompt the user to sign in.

    If used with the authenticate middleware's form method, the path 
    ``/signout`` will display a signed out message if 
    ``authkit.cookie.signout = /signout`` is specified in the config file.

    If used with the authenticate middleware's forward method, the path 
    ``/signin`` should be used to display the sign in form.
    
    The path ``/`` always displays the environment.
    """
    if environ['PATH_INFO']=='/private' and not environ.has_key('REMOTE_USER'):
        start_response('401 Not signed in', [])
    elif environ['PATH_INFO'] == '/signout':
        start_response('200 OK', [('Content-type', 'text/plain')])
        if environ.has_key('REMOTE_USER'):
            return ["Signed Out"]
        else:
            return ["Not signed in"]
    elif environ['PATH_INFO'] == '/signin':
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ["Your application would display a \nsign in form here."]
    else:
        start_response('200 OK', [('Content-type', 'text/plain')])
    return ['%s: %s\n'%(k,v) for k,v in environ.items()]    

