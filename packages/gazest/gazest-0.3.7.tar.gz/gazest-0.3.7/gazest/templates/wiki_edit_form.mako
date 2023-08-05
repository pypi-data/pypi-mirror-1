<%inherit file="wiki_form_base.mako"/>

% if c.show_diff_highlight:

  <h1>Overview of changes</h1>

  Summary: ${"%s insertions(+), %s deletions(-)" % \
             h.diff_stats(c.page.rev, c.editrev)}
 
  <br/>

  ${h.diff_highlight(c.page.rev, c.editrev)}

% endif

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
  
    ## this can be empty but the default will be parsed as an empty
    ## list which is just fine
    <input type="hidden" name="parent_ids" 
           value="${",".join(map(str,c.parent_ids))}"/>

    <input type="submit" name="preview" value="Preview"/>
    <input type="submit" name="save" value="Save"/>
  </p>
  
</form>