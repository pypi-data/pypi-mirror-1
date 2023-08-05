"""Cookie handling based on paste.auth.auth_tkt but with some bug fixes and improvements

Supported cookie options (described in detail in the AuthKit manual)::
    
    cookie_name
    cookie_secure
    cookie_includeip
    cookie_signout
    cookie_secret
    cookie_enforce_expires
    cookie_params = expires 
                    path 
                    comment 
                    domain 
                    max-age 
                    secure 
                    version 

Supported in the middleware but not yet used::
    
    tokens=() 
    user_data=''
    time=None

Features compared to the original paste version:

    #. The authenticate middleware should use authkit version of make_middleware
    #. We need the BadTicket handling in place
    #. We need to be able to use a custom AuthTicket
    #. The custom AuthTicket should accept cookie params specifiable in the config file
    #. The cookie timestamp should be available in the environment as paste.auth_tkt.timestamp

.. Warning ::
    
    You shouldn't rely on the bad ticket or server side expires code because when
    they are triggered, the sign in form isn't displayed. 
    
    Instead it is better to let the cookie expire naturally. For this reason the 
    server side expiration allows a second longer than the cookie expire time so it
    only kicks in if the cookie fails to expire.
    
Here is an example:

.. code-block :: Python

    from paste.httpserver import serve
    from authkit.authenticate import middleware, test_app

    def valid(environ, username, password):
        return username==password

    app = middleware(
        test_app,
        method='form',
        cookie_secret='secret encryption string',
        users_valid=valid,
        cookie_signout = '/signout',
        cookie_params = '''
            expires:10
            comment:test cookie
        ''',
        cookie_enforce = True
    )
    serve(app)

"""

#
# Imports
#

from paste.deploy.converters import asbool
from paste.auth.auth_tkt import *
import os
import time
import logging

#
# Setting up logging
#

log = logging.getLogger('authkit.authenticate.auth_tkt')


#
# Custom AuthKitTicket which allows cookie params like 'expires' etc
#

class AuthKitTicket(AuthTicket):
    """
    This is a standard paste ``AuthTicket`` class except that it also supports a
    ``cookie_params`` dictionary which can have the following options: ``expires``,
    ``path``, ``comment``, ``domain``, ``max-age``, ``secure`` and ``version``.

    .. note ::
    
        Unlike the paste version the ``secure`` option is set as a cookie
        parameter, not on its own.

    The cookie parameters are described in the AuthKit manual under the 
    cookie section.
    """

    def __init__(
        self, 
        secret, 
        userid, 
        ip, 
        tokens=(), 
        user_data='',
        time=None, 
        cookie_name='auth_tkt',
        cookie_params=None
    ):
        secure = False
        if cookie_params is None:
            self.cookie_params = {}
        else:
            # This is a bit of a hack to keep the API consistent with the base classs
            if cookie_params.has_key('secure'):
                secure = asbool(cookie_params.get('secure',False))
                self.cookie_params = {}
                for k, v in cookie_params.items():
                    if k != 'secure':
                        self.cookie_params[k] = v
            else:
                self.cookie_params = cookie_params.copy()
        AuthTicket.__init__(
            self, 
            secret, 
            userid, 
            ip, 
            tokens=tokens,
            user_data=user_data,
            time=time,
            cookie_name=cookie_name,
            secure=secure
        )

    def cookie(self):
        c = Cookie.SimpleCookie()
        # XXX This is a bug?!
        c[self.cookie_name] = self.cookie_value().strip().replace('\n', '')
        for k, v in self.cookie_params.items():
            if k not in ['path', 'expires']:
                c[self.cookie_name][k] = v
        # path and secure are handled differently to keep it consistent with the base class API
        if not self.cookie_params.has_key('path'):
            c[self.cookie_name]['path'] = '/'
        else:
            c[self.cookie_name]['path'] = self.cookie_params['path']
        if self.cookie_params.has_key('expires'):
            time = Cookie._getdate(float(self.cookie_params['expires']))
            log.info(time)
            c[self.cookie_name]['expires'] = time
        if self.secure:
            c[self.cookie_name]['secure'] = 'true'

        return c
        
# The other methods in the paste file, calculate_digest and encode_ip_timestamp are utility methods
# which you shouldn't need to use on their own.

#
# Custom AuthKitCookieMiddleware
#

class AuthKitCookieMiddleware(AuthTKTMiddleware):
    
    """
    Same as paste's ``AuthTKTMiddleware`` except you can choose your own ticket
    class and your cookie is removed if there is a bad ticket. Also features 
    server-side cookie expiration and IP-based cookies.

    The options are all described in detail in the cookie options part of the 
    main AuthKit manual.

    """

    def __init__(
        self,
        app,
        secret, 
        cookie_name='auth_tkt', 
        cookie_params=None,
        include_ip=True, 
        logout_path=None,
        cookie_enforce=False,
        ticket_class=AuthKitTicket
    ):
        secure = False
        if cookie_params.has_key('secure') and asbool(cookie_params['secure']) == True:
            secure = True
        AuthTKTMiddleware.__init__(
            self,
            app,
            secret, 
            cookie_name=cookie_name, 
            # secure not needed!
            secure=secure,
            include_ip=include_ip, 
            logout_path=logout_path,
        )
        self.ticket_class = ticket_class
        self.cookie_params = cookie_params and cookie_params.copy() or {}
        self.cookie_enforce = cookie_enforce
        if self.cookie_enforce and not self.cookie_params.has_key('expires'):
            raise Exception("Cannot enforce cookie expiration since no cookie_params 'expires' has been set")

    def __call__(self, environ, start_response):
        cookies = request.get_cookies(environ)
        if cookies.has_key(self.cookie_name):
            cookie_value = cookies[self.cookie_name].value
        else:
            cookie_value = ''
        if cookie_value:
            if self.include_ip:
                remote_addr = environ['REMOTE_ADDR']
            else:
                # mod_auth_tkt uses this dummy value when IP is not
                # checked:
                remote_addr = '0.0.0.0'
            # @@: This should handle bad signatures better:
            # Also, timeouts should cause cookie refresh
            
            #
            # Start changes from the default
            #
            def bad_ticket_app(environ, start_response, msg=None):
                headers = self.logout_user_cookie(environ)
                headers.append(('Content-type','text/plain'))
                start_response(
                    '401 Not authenticated',
                    headers,
                )
                if not msg:
                    msg = 'Bad cookie, you have been signed out. \n'
                    msg += 'If this problem persists please clear your browser\'s cookies.'
                return [msg]
            try:
                timestamp, userid, tokens, user_data = parse_ticket(
                    self.secret, cookie_value, remote_addr)
            except BadTicket, e:
                if e.expected:
                    log.debug("BadTicket: %s Expected: %s"%(e, e.expected))
                else:
                    log.debug("BadTicket: %s"%e)

                return bad_ticket_app(environ, start_response)
            else:
                now = time.time()
                log.debug("Cookie enforce: %s"%self.cookie_enforce)
                log.debug("Time difference: %s"% str(now-timestamp))
                log.debug("Cookie params expire: %s"%self.cookie_params.get('expires'))
                if self.cookie_enforce and now - timestamp > float(self.cookie_params['expires']) + 1:
                    return bad_ticket_app(environ, start_response, msg="Cookie expired.")
                else:
                    environ['paste.auth_tkt.timestamp'] = timestamp
            
            #
            # End changes from the default
            #
        
            tokens = ','.join(tokens)
            environ['REMOTE_USER'] = userid
            if environ.get('REMOTE_USER_TOKENS'):
                # We want to add tokens/roles to what's there:
                tokens = environ['REMOTE_USER_TOKENS'] + ',' + tokens
            environ['REMOTE_USER_TOKENS'] = tokens
            environ['REMOTE_USER_DATA'] = user_data
            environ['AUTH_TYPE'] = 'cookie'
        set_cookies = []
        def set_user(userid, tokens='', user_data=''):
            set_cookies.extend(self.set_user_cookie(
                environ, userid, tokens, user_data))
        def logout_user():
            set_cookies.extend(self.logout_user_cookie(environ))
        environ['paste.auth_tkt.set_user'] = set_user
        environ['paste.auth_tkt.logout_user'] = logout_user
        if self.logout_path and environ.get('PATH_INFO') == self.logout_path:
            logout_user()
        def cookie_setting_start_response(status, headers, exc_info=None):
            headers.extend(set_cookies)
            return start_response(status, headers, exc_info)
        return self.app(environ, cookie_setting_start_response)

#
# This method uses our new cookie
#

    def set_user_cookie(self, environ, userid, tokens, user_data):
        if not isinstance(tokens, basestring):
            tokens = ','.join(tokens)
        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        # Only these three lines change
        #~ if self.secure != self.cookie_params.get('secure', False) and asbool(self.cookie_params['secure']) or False:
            #~ raise Exception('The secure option has changed before '
                #~ 'we got here. This means the base class has changed '
                #~ 'since this class was written. %r %r'%self.secure, )
        ticket = self.ticket_class(
            self.secret,
            userid,
            remote_addr,
            tokens=tokens,
            user_data=user_data,
            cookie_name=self.cookie_name,
            cookie_params = self.cookie_params
        )
        # @@: Should we set REMOTE_USER etc in the current
        # environment right now as well?
        parts = str(ticket.cookie()).split(':')
        cookies = [(parts[0].strip(), ':'.join(parts[1:]).strip())]
        log.debug(cookies)
        return cookies
        
    def logout_user_cookie(self, environ):
        domain = self.cookie_params.get('domain')
        path = '/'
        if not domain:
            cookies = [
                (
                    'Set-Cookie', '%s=""; Path=%s' % (
                        self.cookie_name, 
                        path
                    )
                ),
            ]
        else:
            cookies = [
                (
                    'Set-Cookie', 
                    '%s=""; Path=%s; Domain=%s' % (
                        self.cookie_name, 
                        path, 
                        domain
                    )
                ),
            ]
        return cookies

