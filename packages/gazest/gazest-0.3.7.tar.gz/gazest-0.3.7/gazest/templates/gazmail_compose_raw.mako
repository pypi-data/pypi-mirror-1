
  <form action="${c.form_action}"
	method="post">
    
    <p>
      <label>
	Recipident username: <br/>
	<input type="text" name="username" size="15"
	       value="${c.to_username or ''}"
	       ${c.to_username and 'readonly' or ''}/>
      </label>
    </p>

    <p>
      <label>
	Subject: <br/>
	<input type="text" name="subject" size="15" 
	       value="${c.subject or ''}"/>
      </label>
      
    </p>

    <p>
      <label>
	Message (in <a
      href="http://en.wikipedia.org/wiki/Markdown">markdown</a>
      format): <br/>
      <textarea name="body" cols="70" rows="10"></textarea>
      </label>
    </p>

    <p>
      ## TODO: preview
      <input type="submit" value="Submit" />
    </p>
    
  </form>
