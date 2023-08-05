  
<%inherit file="base.mak"/>

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
       (<a href="${h.url_for(action='revision_diff', to_id=rev.id)}"
           >diff</a>)
       <br/> on ${h.pretty_date(rev.creat_date)}
       <br/> by ${rev.user and rev.user.username or rev.creat_ip}
     </td>
   </tr>
 % endfor
</table>

