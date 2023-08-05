#  Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gazest.lib.base import *
import routes
from pprint import pprint

class TmplController(BaseController):
    def index(self):
        # Return a rendered template
        #   return render_response('/some/template.html')
        # or, Return a response object
        return Response('Hello World')

    def foo(self):

        c.title = "The ultimate Foo"
        pprint(request.environ['pylons.routes_dict'])
        pprint(routes.request_config().mapper_dict)
        pprint(c.routes_dict)

        return render_response('/simple.mak')
    
    def bar(self):
        return h.redirect_to(controller="/tmpl", 
                             action="foo")
