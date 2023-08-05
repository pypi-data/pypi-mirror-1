  
<h2>New users</h2>
<h3>Create an account, it's free!</h3>

<form action="/register" method="post">

  <p>
    <label>
      Username: <br/>
      <input type="text" name="username" size="15" />
    </label>
  </p>
  
  <p>
    <label>
      ## TODO: use labels for the radio buttons
      <label><input type=radio 
	            name="regtype" 
		    value="email"
		    checked="checked"/>Email</label>
      <label><input type=radio 
	            name="regtype" 
		    value="openid"/>OpenID</label>
      : <br/>
      <input type="text" name="regval" size="15" />
    </label>
  </p>

    <p>
    You can create an account using either an email address or an <a
    href="http://openid.net/">OpenID</a> URL.
  </p>
  

  <p>
    <input type="submit" value="Submit" />
  </p>
  
</form>