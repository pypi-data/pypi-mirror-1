  
<%inherit file="wiki_base.mako"/>

<p>
   You can track modifications to this page through it's <a
   href="${h.url_for(action='page_atom')}">Atom feed</a> <img
   border="0" height="16" width="16" src="/img/feed.png" />.
</p>
<%namespace file="common_defs.mako" import="*"/>

<table cellspacing="0" cellpadding="0" border="0" 
       class="revdag">
 % for i, (rev, a_row, n_row) in enumerate(c.rows):
   <tr>
     % for col in a_row:
       <td>${col}</td>
     % endfor
   </tr>
   <tr>
     % for col in n_row:
       % if i+1<len(c.rows) and col:
         <td class="node">
       % else:
         <td class="lastnode">
       % endif
	 ${col}
       </td>
     % endfor
     <td>
       <a href="${h.url_for(action='past_revision', rev_id=rev.id)}"
	  >${rev.comment or "No comment"}</a>
       ${rev_summary(rev)}
     </td>
   </tr>
 % endfor
</table>

