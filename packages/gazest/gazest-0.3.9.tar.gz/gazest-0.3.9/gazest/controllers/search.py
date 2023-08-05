import logging

from gazest.lib.base import *

log = logging.getLogger(__name__)

class SearchController(BaseController):
    def results(self):
        c.noindex = True
        
        c.search_term = request.params["term"]
        c.title = "Search results for '%s'" % c.search_term

        clauses = [RevNode.body.like("%%%s%%" % word)
                   for word in c.search_term.split()]

        q = Page.query.join("rev").filter(model.and_(*clauses))
        c.pages = list(q.limit(50))
        
        return render("/search_results.mako")
    
