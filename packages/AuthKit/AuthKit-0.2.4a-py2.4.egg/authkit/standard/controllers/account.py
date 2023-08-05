"""Account Controller

This controller handles sign in, sign up, sign out, email password
reminders, password changing, session length changes, security and
email confirmations.

It contains:

    Permission classes
        Can be used to set which permissions a user needs in order to
        have access to particular actions.
        
    FormEncode Validators and Schema
        Used to ensure data entered into forms is valid
        
    Controller Code
        Which handles the user requests.
"""

#
# Imports
#

from pylons import request, c, Response
from pylons.templating import render, render_response
from authkit.standard.controllers.secure import SecureController
from authkit.standard.validators import *
from authkit.standard.permissions import *
import paste.request
import formbuild

class AuthKitAccountController(SecureController):

    #
    # My Account for signed in users
    #

    def __call__(self, environ, start_response):
        match = environ['pylons.routes_dict']
        
    #def __call__(self, **p):


        c.model = self.model
        #t = {}
        #for k,v in request.params.items():
        #    t[k] = v[0]
        c.params = dict(request.params)
        #raise Exception(c.params)
        return SecureController.__call__(self, environ, start_response)
        
    def index(self):
        #raise Exception( ValidSession()())
        return render_response('/'+c.template_dir+'/index.myt')
    index.permissions = ValidSession()
    
    #
    # Publically accessible functionality
    #
    
    def signin(self):
        if c.params.has_key('username') or c.params.has_key('password'):
            #h.log(c.params)
            validator = SignIn()
                       #raise Exception(c.params)
            try:
                results = validator.to_python(c.params, state=c)
            except formencode.Invalid, e:
                # Note error_dict doesn't contain strings
                errors = e.error_dict
                if not e.error_dict:
                    errors = {'password':str(e)}
                c.form = formbuild.Form(defaults=dict(c.params), errors=errors)
                return render_response('/'+c.template_dir+'/signin.myt')
            else:
                self.__signin__(username=results.get('username'))
                    
                return render_response('/'+c.template_dir+'/redirect.myt', 
                    url='/'.join(paste.request.construct_url(
                        request.environ, 
                        with_path_info=False,
                        with_query_string=False
                    ).split('/')[:3])+h.url_for(controller=c.controller_name, action='index'),
                    fragment=True,
                )
                #if c.params.has_key('url') and c.params['url'].split('/')[3:][0] != c.template_dir:
                #    m.comp('/'+c.template_dir+'/redirect.myt', url=c.params['url'])
                #else:
                #    m.subexec('/'+c.template_dir+'/index.myt')
        else:
            keys = {}
            for k, v in c.params.items():
                keys[k] = v
            env = {}
            for k, v in request.environ.items():
                env[k] = v
            if request.environ.has_key('paste.recursive.old_path_info'):
                env['PATH_INFO'] = request.environ['paste.recursive.old_path_info'][-1]
                env['SCRIPT_NAME'] = request.environ['paste.recursive.script_name']
            keys['url'] = paste.request.construct_url(
                env, 
                with_path_info=True,
                with_query_string=True
            )
            h.log(keys['url'] )
            
            c.form = formbuild.Form(defaults=keys)
            return render_response('/'+c.template_dir+'/signin.myt')

    def signout(self):
        r = Response()
        if request.environ.has_key('authkit.user'):
            self.__signout__(request.environ['authkit.user'].username, r)
            r.write(render('/'+c.template_dir+'/signedout.myt'))
        else:
            r.write(render('/'+c.template_dir+'/alreadyout.myt'))
        return r

    def change_password(self):
        if c.params.has_key('password') or c.params.has_key('newpassword') or c.params.has_key('cnewpassword'):
            # We do not want people to be able to change their password if they are not signed in
            if not request.environ.has_key('authkit.user'):
                error = paste.httpexceptions.HTTPForbidden()
                error.title = title
                raise error
                #m.abort('403', 'Not signed in')
            validator = PasswordChange()
            try:
                results = validator.to_python(c.params, state=c)
            except formencode.Invalid, e:
                errors = e.error_dict
                if not e.error_dict:
                    errors = {'password':str(e)}
                k = dict(c.params)
                if k.has_key('ignore_old_password'):
                    del k['ignore_old_password']
                c.form = formbuild.Form(defaults=k, errors=errors)
                return render_response('/'+c.template_dir+'/change_password.myt', **k)
            else:
                user = request.environ['authkit.user']
                user.password=results['newpassword']
                user.active=True
                return render_response('/'+c.template_dir+'/index.myt', title="Password Changed", msg="""
                <p>Your password has been successfuly changed.</p>""")
        else:
            c.form = formbuild.Form()
            return render_response('/'+c.template_dir+'/change_password.myt')

    def confirm(self):
        if c.params.has_key('username') or c.params.has_key('password'):
            validator = SignIn()
            try:
                results = validator.to_python(c.params, state=c)
            except formencode.Invalid, e:
                # Note error_dict doesn't contain strings
                errors = e.error_dict
                if not e.error_dict:
                    errors = {'password':str(e)}
                c.form = formbuild.Form(defaults=dict(c.params), errors=errors)
                return render_response('/'+c.template_dir+'/confirm.myt')
            else:
                c.form = formbuild.Form(defaults=results)
                self.__signin__(username=results.get('username'))
                return render_response(
                    '/'+c.template_dir+'/change_password.myt', 
                    msg="""
                        <p>Your email address has been successfuly confirmed. 
                        You can now set your own password.</p>""",
                    title="Email Confirmed",
                    ignore_old_password=True,
                )
        else:
            c.form = formbuild.Form()
            return render_response('/'+c.template_dir+'/confirm.myt')
            
    def create(self):
        if len(dict(c.params)):
            validator = FullResgistration()
            try:
                results = validator.to_python(c.params, state=c)
                if len(c.model.User.mapper.select_by(username=results['email'])):
                    raise formencode.Invalid('User already exists')
            except formencode.Invalid, e:
                errors = e.error_dict
                if not e.error_dict:
                    errors = {'password':str(e)}
                c.form = formbuild.Form(defaults=dict(c.params), errors=errors)
                return render_response('/'+c.template_dir+'/signup.myt')
            else:
                results['password'] = self._gen_passwd()
                c.confirm_url = '/'.join(paste.request.construct_url(
                    request.environ, 
                    with_path_info=False,
                    with_query_string=False
                ).split('/')[:3])+h.url_for(controller=c.controller_name, action='confirm')
                        
                msg = render('/'+c.template_dir+'/email_confirm_msg.myt', fragment=True, **results)
                newuser = c.model.User(
                    username=results['email'], 
                    firstname=results['firstname'], 
                    surname=results['surname'], 
                    active=False,
                    password=results['password'],
                )
                h.mail(
                    to = [results['email']],
                    subject = request.environ['paste.config']['app_conf']['confirm_email_subject'],
                    smtp = request.environ['paste.config']['global_conf']['smtp_server'],
                    sendmail = request.environ['paste.config']['global_conf']['sendmail'],
                    method = request.environ['paste.config']['global_conf']['method'],
                    reply = request.environ['paste.config']['app_conf']['email_from'],
                    msg = msg,
                )
                return render_response('/'+c.template_dir+'/confirmation_sent.myt', **results)
        else:
            c.form = formbuild.Form()
            return render_response('/'+c.template_dir+'/signup.myt')

    def password(self):
        if c.params.has_key('email'):
            validator = PasswordReminder()
            try:
                results = validator.to_python(c.params, state=c)
            except formencode.Invalid, e:
                errors = e.error_dict
                if not e.error_dict:
                    errors = {'password':str(e)}
                c.form = formbuild.Form(defaults=dict(c.params), errors=errors)
                return render_response('/'+c.template_dir+'/password_reminder.myt')
            else:
                user = c.model.User.mapper.select_by(username=results['email'].lower())[0]
                c.signin_url = '/'.join(paste.request.construct_url(
                    request.environ, 
                    with_path_info=False,
                    with_query_string=False
                ).split('/')[:3])+h.url_for(controller=c.controller_name, action='signin')
                msg = render(
                    '/'+c.template_dir+'/email_password_reminder_msg.myt', 
                    firstname=user.firstname, 
                    password=user.password, 
                    email=user.username,
                    fragment=True,
                )
                h.mail(
                    to = [user.username],
                    subject = request.environ['paste.config']['app_conf']['password_reminder_subject'],
                    smtp = request.environ['paste.config']['global_conf']['smtp_server'],
                    sendmail = request.environ['paste.config']['global_conf']['sendmail'],
                    method = request.environ['paste.config']['global_conf']['method'],
                    reply = request.environ['paste.config']['app_conf']['email_from'],
                    msg = msg,
                )
                return render_response('/'+c.template_dir+'/password_reminder_sent.myt', email=user.username)
        else:
            c.form = formbuild.Form()
            return render_response('/'+c.template_dir+'/password_reminder.myt')


    #
    # Private methods
    #
    
    def _gen_passwd(self):
        t = md5.new()
        t.update('this is a test of the emergency broadcasting system')
        r = random.Random(str(time.time()))
        t.update(str(r.random()))
        s = base64.encodestring(t.digest())[:-3].replace('/', '$')
        s = s.replace('+','p')
        s = s.replace('$','d')
        s = s.replace('\\','b')
        s = s.replace('/','f')
        return s[:8]
            
            
