<h1>Password Reminder</h1>
<h2>Please enter your email address below to be emailed a password reminder.</h2>
<% c.form.start(name="signin", action=h.url_for(controller=c.controller_name, action="password"), method="post", onSubmit="return jcap();") %>
<fieldset>
    <legend>Send Password Reminder</legend>
    <p>
      <label for="surname">Account Email Address:<br />
      <% c.form.get_error('email', format='<span class="error">%s</span>') %></label>
      <% c.form.field.text(name="email", class_="txt", id="email") %>
    </p>
   <br />
  </fieldset>
  <p>&nbsp;</p>
    <input type="submit" name="btnSubmit" id="btnSubmit" value="Send Reminder" class="yellowbuttonvbig" />
  </p>
</form>
