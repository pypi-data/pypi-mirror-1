Dear <% ARGS['firstname'] %>,

You have requested a password reminder. Your password is below:

Password: <% ARGS['password'] %>

You can now sign in at the URL below with the email address <% ARGS['email'] %>:

<% c.signin_url %>

Regards