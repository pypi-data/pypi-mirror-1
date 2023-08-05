
<%def name="readonly_warning()">
 <% h.m_warn("The site is in read only mode."
             " What you are about to do will probably fail.") 
  %>
</%def>

<%def name="rev_atom_full(rev)">

 <entry>
   <% 
      gain, lost, ratio = h.diff_stats(rev.parents()[-1], rev)
      by = rev.user and rev.user.username or rev.creat_ip
    %>
   <updated>${rev.creat_date.isoformat()}Z</updated>
   <title>
     ${rev.slug}: ${rev.comment or "No Comment"} 
     by ${by}
     ${"(%d+, %d-, %.1f%%)" % (gain, lost, ratio*100)}
   </title>
   <author>
     <name>${by}</name>
   </author>
   <id>${rev.taguri()}</id>

   <content type="xhtml">
     <div xmlns="http://www.w3.org/1999/xhtml">
       ## TODO: side by side would be nice but there is no CSS in Atom
       ${h.diff_html_unified(rev.parents()[-1], rev)}
     </div>
   </content>

   <link href="${h.fq_url_for(action='revision_diff', \
	                      to_id=rev.id, slug=rev.slug)}"/>
 </entry>

</%def>


<%def name="rev_atom_creat(rev)">
 ## use this def for revisions without parents
 <entry>
   <% 
      by = rev.user and rev.user.username or rev.creat_ip
    %>
   <updated>${rev.creat_date.isoformat()}Z</updated>
   <title>
     ${rev.slug}: ${rev.comment or "No Comment"} 
     by ${by}
     ${"(%d+, 0-, 100.0%%)" % (len(rev.body.split("/n")))}
   </title>
   <author>
     <name>${by}</name>
   </author>
   <id>${rev.taguri()}</id>

   <content type="xhtml">
     <div xmlns="http://www.w3.org/1999/xhtml">
       <pre>${rev.body|h}</pre>
     </div>
   </content>

   <link href="${h.fq_url_for(action='past_revision', \
	                      rev_id=rev.id, slug=rev.slug)}"/>
 </entry>

</%def>


<%def name="rev_diff_stats(rev)">
  <%
    if rev.parents():
      gain, lost, ratio = h.diff_stats(rev.parents()[-1], rev) 
    else:
      gain, lost, ratio = len(rev.body.split("/n")), 0, 1.0
   %>
  ${"(%d+, %d-, %.1f%%)" % (gain, lost, ratio*100)}
</%def>


<%def name="rev_summary(rev)">
  ## The caller is expected to print the title
  ${h.rev_actions(rev)}
  <br/> on ${h.pretty_date(rev.creat_date)}
  by ${rev.user and rev.user.username or rev.creat_ip}
  ${rev_diff_stats(rev)}
</%def>


<%def name="changes_summary(from_rev, to_rev)">
<% gain, loss, ratio = h.diff_stats(from_rev, to_rev) %>
<p>
Summary: 
  <ul>
    <li>${gain} insertions (+)</li>
    <li>${loss} deletions (-)</li>
    <li>${"%.1f%%" % (ratio * 100)} changes/content ratio</li>
  </ul>
</p>
</%def>
