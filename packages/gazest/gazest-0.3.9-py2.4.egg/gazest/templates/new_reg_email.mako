From: ${c.from_addr}
To: ${c.to_addr}
Subject: ${c.subject or "New %s user: email confirmation request" % h.site_name()}


Hi there, 
  I'm the account creation bot for ${h.site_name()}.

A ${h.site_name()} user account have been requested with your email
address as the main contact.  If this is OK with you, just follow the
link below and setup your password and profile.

  ${c.conf_url}

If you never requested a user account on ${h.site_name()}, just ignore
this email.  We will not contact you again regarding this request.

Yours truly, 

--
The account creation bot

