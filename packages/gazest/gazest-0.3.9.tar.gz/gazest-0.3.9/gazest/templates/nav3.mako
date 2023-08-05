
<%!

from authkit.pylons_adaptors import authorized
from authkit.permissions import RemoteUser, RequestPermission

%>

## This is a bit more tricky since there could be no level 3 nav actions
## at all

% if c.nav3_actions:

<div class="nav3">
  <ul>
    % for label, cont, action in c.nav3_actions:
    
      <li><a href="${h.url_for(controller=cont, action=action)}"
	     ${(c.routes_dict["action"]==action and \
	        c.routes_dict["controller"]==cont.strip("/")) \
	       and 'class="selected"' or ''}
	     >${label}</a></li>
    
    % endfor
  </ul>
</div>

% endif
