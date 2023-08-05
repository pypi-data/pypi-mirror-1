  
<%inherit file="wiki_base.mako"/>

<h2>Revisions recently flagged as abusive</h2>

<table>
 % for rev, count in c.rev_rep_pairs:
   <tr>
     <td>
       <a href="${h.url_for(action='view', slug=rev.slug)}">${rev.slug}</a>: 
       <a href="${h.url_for(action='past_revision', rev_id=rev.id, slug=rev.slug)}"
	  >${rev.comment or "No comment"}</a>
       % if rev.parents():
         (<a href="${h.url_for(action='revision_diff', to_id=rev.id, slug=rev.slug)}"
             >diff</a> 
	 |
<a href="${h.url_for(action='diff_form', slug=rev.slug)}"
             >hist</a> 
	 |
	 <a href="${h.url_for(action='undo_revision', rev_id=rev.id, slug=rev.slug)}"
	    >undo</a>
	 |
	 <a href="${h.url_for(action='boycott_form', addr=rev.creat_ip)}"
	    >ban</a>)
       % endif
       <br/> on ${h.pretty_date(rev.creat_date)}
       <br/> by ${rev.user and rev.user.username or rev.creat_ip}
       <br/> reported <strong>${count}</strong> times.
     </td>
   </tr>
 % endfor
</table>

% if not c.rev_rep_pairs:
  Nothing to see here.  Move along.
% endif
