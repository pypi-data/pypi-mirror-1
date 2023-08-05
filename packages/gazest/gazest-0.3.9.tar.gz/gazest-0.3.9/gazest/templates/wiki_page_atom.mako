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

<%namespace file="common_defs.mako" import="*"/>
% for rev in c.revs:
 % if rev.parents():
   ${rev_atom_full(rev)}
 % else:
   ${rev_atom_creat(rev)}
 % endif
% endfor

</feed>
