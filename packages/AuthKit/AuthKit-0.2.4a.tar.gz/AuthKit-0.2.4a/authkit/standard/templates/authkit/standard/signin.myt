<h1>Login to Account</h1>
<% c.form.start(name="signin", action=h.url_for(controller=c.controller_name, action="signin"), method="post") %>
<fieldset>
    <legend>Login</legend>

    <p>
      <label for="email">Email Address (User Name):<br />
      <% c.form.get_error('username', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="username", class_="txt", id="email") %>
    </p>
    <p>
      <label for="password">Password:<br />
      <% c.form.get_error('password', format='<span class="error">%s</span>') %></label>
      <% c.form.field.password(name="password", value='', class_="txt", id="password") %>
    </p>

<br />
<h3>Create Account</h3>
<p>If you dont have an account, create one <a href="<% h.url_for(controller=c.controller_name, action='create') %>"><strong>here</strong></a>
<h3>Forgot Password?</h3>
<p>I forgot my password, please <a href="<% h.url_for(controller=c.controller_name, action='password') %>"><strong>email it to me</strong></a>
</fieldset>
  <p>&nbsp;</p>
    <input type="submit" name="btnSubmit" id="btnSubmit" value="Login" class="yellowbutton" />
  </p>
<% c.form.end() %>
