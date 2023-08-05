  
<%inherit file="base.mako"/>

<p>
  Summary: ${"%s insertions(+), %s deletions(-)" % \
             h.diff_stats(c.from_rev, c.to_rev)}
</p>

${h.diff_highlight(c.from_rev, c.to_rev)}

