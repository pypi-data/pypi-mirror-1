<h1>Confirmation Sent</h1>

<p>A confirmation email containing your password has been sent to <% ARGS['email'] %>. </p>

<p>Please check your email and then <% h.link_to('confirm your email address', h.url_for(controller=c.controller_name, action='confirm')) %> by following the instructions in the email.</p>
