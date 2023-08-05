<h1>Password Reminder Sent</h1>

<p>A password reminder has been sent to the email address <% ARGS['email'] %>.</p>

<p>Please check your email and then <% h.link_to( 'sign in',h.url_for(controller=c.controller_name)) %>. </p>
