<%inherit file="base.mak"/>

% if c.preview:

  <h1>Page preview</h1>

  ${c.preview}

% endif

<h1>Edit page</h1>

<form action="${h.url_for(action='edit_action')}" method="post">

  <p>
    
    <label>
      
      Body (in markdown+wiki format):<br/>

      <textarea name="body" cols="70" rows="10">${c.body or ''}</textarea>

    </label>

  </p>

  <p>
    
    <label>
      
      Summary of changes:<br/>

      <input type="text" name="comment" size="70"
	     value="${c.comment or ''}"/>

    </label>

  </p>


  <p>
% if c.parent_id:    
    <input type="hidden" name="parent_id" value="${c.parent_id}"/>
% endif

    <input type="submit" name="preview" value="Preview"/>
    <input type="submit" name="save" value="Save"/>
  </p>
  
</form>