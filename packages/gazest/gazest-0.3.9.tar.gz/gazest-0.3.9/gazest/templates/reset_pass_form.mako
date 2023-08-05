<%inherit file="form_base.mako"/>

<h1>Set your new password</h1>

<form action="${c.form_action}" method="post">
  
  <p>
      <label>New password: <br/>
      <input type="password" name="password"/></label>

  </p>

  <p>
      <label>New password (retype): <br/>
      <input type="password" name="password_confirm"/></label>

  </p>

  <p>
    <input type="submit"/>
  </p>

</form>
