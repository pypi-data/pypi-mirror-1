
## Populate with h1, h2, p and div.  It does the right thing.

<%def name="sidebar()">
  <div class="sidebar">
    ${caller.body()}
  </div>
</%def>
