  
<%inherit file="base.mako"/>

## TODO: there is much to improve here

<h1>${c.title}</h1>

<ul>
  % for page in c.pages:
 
  <li>
    <a href="${h.url_for(controller='/wiki', action='view', slug=page.slug)}"
       >${page.slug}</a>
  </li>

  % endfor  
</ul>

% if not c.pages:
  <p>No pages found.</p>
% end if