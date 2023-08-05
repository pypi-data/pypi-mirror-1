  
<%inherit file="base.mak"/>

<h1>Jump into the system</h1>

<h2>Existing users</h2>

<div style="float:left;clear:right;width:50%">
  <h3>Password users</h3>
  <%include file="login_email_raw.mak" />
</div>
 
<div style="float:left;clear:right;width:50%">
  <h3>OpenID users</h3>
  <%include file="login_openid_raw.mak" />
</div>



<hr style="clear: both;"/>

## TODO: use the two column layout
<%include file="registration_raw.mak" />
  
