<h1>User Registration Form</h1>

<% c.form.start(name="signin", action=h.url_for(controller=c.controller_name, action="create"), method="post", onSubmit="return jcap();") %>
<fieldset>
    <legend>Create Login Name</legend>
    <p>
      <label for="firstname">First Name:<br />
      <% c.form.get_error('firstname', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="firstname", class_="txt", id="firstname") %>
    </p>
    <p>
      <label for="surname">Surname:<br />
      <% c.form.get_error('surname', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="surname", class_="txt", id="surname") %>
    </p>
    <p>&nbsp;</p>
    <p>
      <label for="surname">Email Address (*User Name):<br />
      <% c.form.get_error('email', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="email", class_="txt", id="email") %>
    </p>
    <p>
      <label for="surname">Confirm Email Address:<br />
      <% c.form.get_error('cemail', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="cemail", class_="txt", id="cemail") %>
    </p>
    
  </fieldset>
  <p>&nbsp;</p>
    <input type="submit" name="btnSubmit" id="btnSubmit" value="Verify Email Address!" />
  </p>
</form>
