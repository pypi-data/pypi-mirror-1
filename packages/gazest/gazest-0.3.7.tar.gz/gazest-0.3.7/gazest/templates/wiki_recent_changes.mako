  
<%inherit file="wiki_base.mako"/>

<p>
   You can track changes to this site through the <a
   href="${h.url_for(controller='/wiki', action='site_atom')}">changes
   Atom feed</a> <img border="0" height="16" width="16"
   src="/img/feed.png" />.
</p>

<table>
 % for rev in c.revs:
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
	 <a href="${h.url_for(action='abuse_report_form', rev_id=rev.id, slug=rev.slug)}"
	    >report abuse</a>)
       % endif
       <br/> on ${h.pretty_date(rev.creat_date)}
       <br/> by ${rev.user and rev.user.username or rev.creat_ip}
     </td>
   </tr>
 % endfor
</table>

% if not c.revs:
  Nothing to see here.  Move along.
% endif
