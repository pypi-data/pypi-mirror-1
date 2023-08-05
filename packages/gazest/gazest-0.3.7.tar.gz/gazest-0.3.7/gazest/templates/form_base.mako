<%inherit file="base.mako"/>

## This template should be the parent of any form that leads to a
## write action.  It provides proper warnings while switching to
## read-only mode or during a soft-ban.

<%def name="readonly_msg()">
  ${self.common.readonly_warning()}
</%def>

${next.body()}
