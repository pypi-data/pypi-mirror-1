  
<%inherit file="base.mako"/>
<%namespace file="common_defs.mako" import="*"/>
${changes_summary(c.from_rev, c.to_rev)}

${h.diff_highlight(c.from_rev, c.to_rev)}

