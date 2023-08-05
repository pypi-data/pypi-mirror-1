AuthKit
+++++++

WARNING: THIS CODE IS NOT PRODUCTION READY

AuthKit is a Pylons Extension Package to add secrity functionality to Pylons.

Changes
=======

0.1 
	Based on the web.auth 0.6 module from www.pythonweb.org, support for SQLObject driver included
	
0.2
	Re-written from scratch so to use SQLAlchemy only, old driver system considered unnecessary and limiting. Also doesn't fit in with current Pylons best-practice.


Take it away!
=============

This is how to apply the current authkit to a new project named ``clickywiki``. Incidentally clickywiki is one of James Gardner's current projects written in Pylons. 

Create your project:
	> paster create --template=pylons clickywiki

Add this to models/__init__.py
	from authkit.standard.models import *

Add the sign in middleware to config/middleware::

	# at the top of the file:
	from authkit.standard.middleware import authkit_form

	# YOUR MIDDLEWARE
	# Put your own middleware here, so that any problems are caught by the error
	# handling middleware underneath

	app = authkit_form(
		app, 
		global_conf,
		secret=app_conf['session_secret'],
		cookie_name='auth_tkt',
		secure=False,
		include_ip=True,
		sign_out_path='/account/sign_out',
		sign_in_path='/account/signin',
	)

Add the SQLAlchemy DSN to the development.ini file:
	dsn = mysql://database=test

While you're at it add these keys too:
	email_from = James Gardner <james@pythonweb.org>
	confirm_email_subject = Confirmation
	password_reminder_subject = Password Reminder
	
And add these to the global_conf:
	sendmail = /usr/sbin/sendmail
	smtp_server = smtp.bulldogdsl.com
	method = sendmail

or to send via SMTP:
	method = smtp
	
Create a script called ``setup_tables.py`` in the same level as ``setup.py`` to create the database tables remembering to change ``clickywiki`` to the appropriate name for your app and specify the correct config file to ``appconfig()``:
			
	#!/usr/bin/python

	import os

	import sqlalchemy
	from paste.deploy import appconfig
	from opentelcom.models import *

	app_conf = appconfig('config:development.ini', relative_to=os.getcwd())
	sqlalchemy.global_connect(app_conf['dsn'])

	Group.table.create()
	User.table.create()
	History.table.create()
	App.table.create()
	Role.table.create()
	Permission.table.create()

	sqlalchemy.objectstore.commit()

	g = Group('Everyone')
	r = Role('Role')
	a = App('Admin')
	sqlalchemy.objectstore.commit()
	u = User(user='admin@example.com',password='admin')
	sqlalchemy.objectstore.commit()
	p = Permission(user=1,app=1,role=1)
	sqlalchemy.objectstore.commit()

Copy templates from authkit/standard/templates
Copy components from authkit/standard/components
Delete clickywiki/components/empty.myc (it isn't needed)

Create controller:
	> cd clickywiki
	> paster controller account

Edit it to be like this, relpacing ``clickywiki`` with the name of your app::


	from clickywiki.lib.base import *
	from authkit.standard.controllers.account import AuthKitAccountController

	class AccountController(AuthKitAccountController):
	    model = model

Install the web module for sending email:

	> easy_install web

Edit lib/helpers.py to use web.mail and web.util.time.seconds

	from webhelpers import *
	from web.mail import send as mail
	from web.util.time import seconds

Add this to account/index.myt instead of the main links (no whitespace before the start of each line):

	<%python>
	from authkit.standard.permissions import ValidSession, And, UserAndHasPermission
	import clickywiki.models as model
	</%python>

	<ul>
	<li><% h.link_to('Change your password', h.url_for(controller='account', action='change_password')) %></li>
	<li><% h.link_to('Change your session length', h.url_for(controller='account', action='change_session')) %></li>
	<li><% h.link_to('Sign Out', h.url_for(controller='account', action='signout')) %></li>

	% if And(UserAndHasPermission(model, app='Admin'), ValidSession())():
	<li><% h.link_to("Admin", h.url_for(controller="account", action="admin")) %></li>
	% #endif
	</ul>

Next you need to setup your admin controllers

	Copy from \scaffold\standard\templates\standard to scaffold/templates/standard

Create a user controller that looks like this::

	from clickywiki.lib.base import *
	from authkit.standard.controllers.account import AuthKitAccountController
	from authkit.standard.permissions import *
	from authkit.standard.controllers.secure_scaffold import Secure_ScaffoldController, Lookup
	import formbuild

	admin_permissions = And(UserAndHasPermission(model, app='Admin'), ValidSession())

	class AccountController(AuthKitAccountController):
	    model = model
	    admin_permissions = admin_permissions
	    
	    def __before__(self, action):
		c.security = c.account = 'account'
		c.model = model

	    def admin(self, table=None, subaction=None, **kargs):
		if table == None:
		    m.subexec('account/admin.myt')
		else:
		    c.model = self.model
		    c.url_map = {
			'action':'subaction',
			'controller':'table',
		    }
		    c.exclude = ['uid']
		    c.foreign_key_values = {}
		    c.foreign_key_lookup = {}
		    if table == 'user':
			c.name = 'User'
			c.exclude = ['active', 'uid']
			c.foreign_key_values = {
				'group': [tuple([x.uid, x.name]) for x in c.model.Group.mapper.select()]
			    }
			c.foreign_key_lookup = {
				'group': Lookup(c.model.Group, 'uid', 'name')
			    }
		    elif table in ['app','role','group']:
			c.name = table.capitalize()
		    elif table == 'permission':
			c.name = 'Permission'
			c.foreign_key_values = {
			    'user': [tuple([x.uid, x.user]) for x in model.User.mapper.select()],
			    'app': [tuple([x.uid, x.name]) for x in model.App.mapper.select()],
			    'role': [tuple([x.uid, x.name]) for x in model.Role.mapper.select()],
			}
			c.foreign_key_lookup = {
			    'user': Lookup(model.User, 'uid', 'user'),
			    'app': Lookup(model.App, 'uid', 'name'),
			    'role': Lookup(model.Role, 'uid', 'name'),
			}
		    else:
			m.abort(404, 'Scaffold table not found')

		    class AutoGeneratedController(Secure_ScaffoldController):
			model=model
			def __before__(self, action):

			    c.template = '/scaffold/templates/standard/'
			    c.table = getattr(c.model,c.name).mapper.table.name
			    c.form = formbuild.Form()
		    del kargs['action']
		    return AutoGeneratedController()(subaction, **kargs)
	    admin.permissions = admin_permissions

Add some helpers to lib/helpers.py at the end::

	def translated_url(translation_map, **p):
		final = {}
		for k, v in p.items():
			if translation_map.has_key(k):
				final[translation_map[k]] = v
			else:
				final[k] = v
		return url(**final)


	def translated_redirect_to(translation_map, **p):
		final = {}
		for k, v in p.items():
			if translation_map.has_key(k):
				final[translation_map[k]] = v
			else:
				final[k] = v
		return redirect_to(**final)
	
Define your routes in config/routing.py:

	map.connect(':controller/:action')
	map.connect(':controller/:action/:id',id=None)
	map.connect('account/admin/:table/:subaction/:id', controller='account', action='admin')
	map.connect('*url', controller='template', action='view')

Then add in CloseConnection filter if running FastCGI
    
I think that should be it! Good luck!

Create your tables and start your server

	> python setup_tables.py
	> paster serve --reload development.ini
	
You can now sign in with admin@example.com and pasword ``admin`` since these were the details added by ``setup_tables.py``.

James
