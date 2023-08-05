
## Print user messages, as colored divs, before the content

% if c.m_info or session.get("m_info"):
  <div class="m_info">
    <ul>
     % for msg in c.m_info:
       <li>${msg}</li>
     % endfor 

     % if session.get("m_info"):
     <%
      ## FIXME: there is a race condition
      flashes = session["m_info"]
      session["m_info"] = []
      session.save()
     %>
     % for msg in flashes:
       <li>${msg}</li>
     % endfor
     % endif
     
    </ul>
  </div>
% endif

% if c.m_warn or session.get("m_warn"):
<div class="m_warn">
    <ul>
     % for msg in c.m_warn:
       <li>${msg}</li>
     % endfor 

     % if session.get("m_warn"):
     <%
      ## FIXME: there is a race condition
      flashes = session["m_warn"]
      session["m_warn"] = []
      session.save()
     %>
     % for msg in flashes:
       <li>${msg}</li>
     % endfor
     % endif
     
    </ul>
  </div>
% endif
