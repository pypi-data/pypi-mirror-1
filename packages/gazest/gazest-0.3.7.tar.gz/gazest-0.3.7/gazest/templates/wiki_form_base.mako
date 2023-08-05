
<%inherit file="wiki_base.mako"/>

<%def name="readonly_msg()">
  ${self.common.readonly_warning()}
</%def>

${next.body()}
