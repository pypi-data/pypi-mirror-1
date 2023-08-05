  
<%inherit file="base.mako"/>

<h1>Message from ${c.gazmail.from_user.username}</h1>

<%include file="nav3.mako" />

<h2>${c.gazmail.subject}</h2>

${c.gazmail.render_body()}

## TODO: make a pluggable action that can fit in many places
## <%include file="nav3.mako" />
