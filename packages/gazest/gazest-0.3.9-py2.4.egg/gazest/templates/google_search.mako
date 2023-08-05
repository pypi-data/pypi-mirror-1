
## Site admins will probably want to replace this with a custom search
## box that they can create from their Google AdSense account.  Among
## other things, the custom search box gives the site admin ad
## revenues on impressions and clicks

<form action="http://www.google.com/search" method="get">
  <input type="text" name="q"></input>
  <input type="hidden" name="sitesearch" 
	 value="${g.config['site_base']}"/>
  <input type="submit" value="Search"></input>
</form>
