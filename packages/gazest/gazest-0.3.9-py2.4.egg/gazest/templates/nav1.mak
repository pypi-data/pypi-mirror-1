
<%!

from authkit.pylons_adaptors import authorized
from authkit.permissions import RemoteUser, RequestPermission

%>

<div class="nav1">
  <ul>
    % if authorized(RemoteUser()):
      <li>You are <a href="/u/${request.environ["REMOTE_USER"]}"
          >${request.environ["REMOTE_USER"]}</a></li>
    % endif

    % for label, cont, action in c.nav1_actions:
    
      <li><a href="${h.url_for(controller=cont, action=action)}"
	     ${(c.routes_dict["action"]==action and \
	        c.routes_dict["controller"]==cont.strip("/")) \
	       and 'class="selected"' or ''}
	     >${label}</a></li>
    
    % endfor

  </ul>
</div>
