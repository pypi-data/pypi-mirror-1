
<%inherit file="form_base.mako"/>

<h1>Reply to ${c.parent_gazmail.from_user.username}</h1>
<%include file="nav3.mako" />

<h2>${c.parent_gazmail.subject}</h2>
${c.parent_gazmail.render_body()}

<h2>Your reply</h2>
<hr/>
<%include file="gazmail_compose_raw.mako" />


## TODO: quote the replied message
## TODO: make the to_username look more disabled