
<div class="nav2">
  <ul>
    % for label, cont, action in c.nav2_actions:
    
      <li><a href="${h.url_for(controller=cont, action=action)}"
	     ${(c.routes_dict["action"]==action and \
	        c.routes_dict["controller"]==cont.strip("/")) \
	       and 'class="selected"' or ''}
	     >${label}</a></li>
    
    % endfor

  </ul>
</div>
