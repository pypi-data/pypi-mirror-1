<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

 <title>${h.site_name()}: ${c.page.slug} page revision feed</title>
 <link rel="alternate" href="${h.site_base()}"/>
 <link rel="self" href="${h.fq_url_for(action='page_atom')}"/>
 <icon>${h.site_base()}/favicon.ico</icon>

 <updated>${max([rev.creat_date for rev in c.revs]).isoformat()}Z</updated>
 <author>
   <name>${g.config["copyright_owner"]}</name>
   <email>${g.config["copyright_owner_email"]}</email>
 </author>

 <id>${c.page.taguri()}</id>

% for rev in c.revs:
 <entry>
   <updated>${rev.creat_date.isoformat()}Z</updated>
   <title>${rev.comment or "No Comment"}</title>
   <author>
     <name>${rev.user and rev.user.username or rev.creat_ip}</name>
##   <email>${g.config["copyright_owner_email"]}</email>
   </author>

   <content type="xhtml">
     <div xmlns="http://www.w3.org/1999/xhtml">
       % if rev.parents():
         ## TODO: side by side would be nice but there is no CSS in Atom
         <pre>${h.diff_unified(rev.parents()[-1], rev).replace("\n", "<br/>")}
	 </pre>
       % else:
         <pre>${rev.body}</pre>
       % endif

     </div>
   </content>

   <link href="${h.fq_url_for(action='revision_diff', to_id=rev.id)}"/>
   <id>${rev.taguri()}</id>
 </entry>
% endfor

</feed>
