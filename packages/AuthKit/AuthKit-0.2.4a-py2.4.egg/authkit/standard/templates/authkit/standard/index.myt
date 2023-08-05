
<h1>
<%python>
if ARGS.has_key('title'):
	m.write(ARGS['title'])
else:
	m.write("""My Account""")
</%python>
</h1>
<p>&nbsp;</p>
<%python>

if ARGS.has_key('msg'):
	m.write(ARGS['msg'])
else:
	m.write("""
	<p>Welcome to the My Account area. From here you can do the following:</p>
	""")
</%python>

<ul>
<li><% h.link_to('Change your password', h.url_for(controller=c.controller_name, action='change_password')) %></li>
<li><% h.link_to('Sign Out', h.url_for(controller=c.controller_name, action='signout')) %></li>
</ul>
