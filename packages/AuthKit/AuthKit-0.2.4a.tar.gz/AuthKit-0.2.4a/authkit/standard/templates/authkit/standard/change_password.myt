<h1>
	<%python>
	if ARGS.has_key('title'):
		m.write(ARGS['title'])
	else:
		m.write('Change Password')
	</%python>

</h1>

<%python>
if ARGS.has_key('msg'):
	m.write(ARGS['msg'])
</%python>

<% c.form.start(name="signin", action=h.url_for(controller=c.controller_name, action='change_password'), method="post", onSubmit="return jcap();") %>
<fieldset>
    <legend>Change Password</legend>

% if not ARGS.has_key('ignore_old_password'):
    <p>
      <label for="email">Current Password:<br />
      <% c.form.get_error('password', format='<span class="error">%s</span>') %></label>
      <% c.form.field.password(name="password", class_="txt", id="email") %>
    </p>
    
% else:
	<% c.form.field.hidden(name="password") %>
	<% c.form.field.hidden(name="ignore_old_password", value=1) %>
% #endif

    <p>
      <label for="password">Password:<br />
      <% c.form.get_error('newpassword', format='<span class="error">%s</span>') %></label>
      <% c.form.field.password(name="newpassword", value='', class_="txt", id="newpassword") %>
    </p>
    <p>
      <label for="password">Password Confirm:<br />
      <% c.form.get_error('cnewpassword', format='<span class="error">%s</span>') %></label>
      <% c.form.field.password(name="cnewpassword", value='', class_="txt", id="cnewpassword") %>
    </p>
<br />
</fieldset>
  <p>&nbsp;</p>
  
    <input type="submit" name="btnSubmit" id="btnSubmit" value="Submit" class="yellowbutton" />
  </p>
<% c.form.end() %>
