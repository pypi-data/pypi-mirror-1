  
<%inherit file="wiki_base.mako"/>

<p>
   You can track changes to this site through the <a
   href="${h.url_for(controller='/wiki', action='site_atom')}">changes
   Atom feed</a> <img border="0" height="16" width="16"
   src="/img/feed.png" />.
</p>

<%namespace file="common_defs.mako" import="*"/>

<%def name="rev_tr(rev, full=False)">
  <tr>
    <td></td>
    % if full:
      <td><a href="${h.url_for(action='view', slug=rev.slug)}"
	     >${rev.slug}</a></td>
    % else:
      <td></td>
    % endif
    
    <td>${rev.creat_date.strftime("%R")}</td>
    <td>${rev.user and rev.user.username or rev.creat_ip}</td>
    <td>
      <a href="${h.url_for(action='past_revision', rev_id=rev.id, slug=rev.slug)}"
	  >${rev.comment or "No comment"}</a>
      <br/> ${rev_diff_stats(rev)} ${h.rev_actions(rev)}

    </td>
    
  </tr>
</%def>

<table class="changeslog">
  % for date, subgroups in c.groups:
    <tr><th>${date}</th></tr>
    % for slug, revs in subgroups:
      ${rev_tr(revs[0], True)}
      % for rev in revs[1:]:
        ${rev_tr(rev)}
      % endfor
    % endfor
  % endfor
</table>

% if not c.revs:
  Nothing to see here.  Move along.
% endif
