
<form action="${h.url_for(controller='/search', action='results')}" 
      method="get">
  <input type="text" name="term" value="${c.search_term}"></input>
  <input type="submit" value="Search"></input>
</form>

