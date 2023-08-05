  
<%inherit file="form_base.mako"/>

<h1>Update user profile</h1>

  <form action="/user_profile_edit_action" method="post">
    
    <p>
      <label>
	Email address: <br/>
	<input type="text" name="email" size="15" />
      </label>
    </p>

    <p>
      <label>
	Password: <br/>
	<input type="password" name="password" size="15" />
      </label>
      
    </p>


    <p>
      <input type="submit" value="Submit" />
    </p>
    
  </form>
