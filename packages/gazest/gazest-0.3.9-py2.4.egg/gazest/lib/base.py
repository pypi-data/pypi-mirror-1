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

"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render
from pylons.database import make_session

import gazest.lib.helpers as h
import gazest.model as model
from gazest.model import *
from gazest import __version__

from authkit.pylons_adaptors import authorized
from authkit.permissions import RemoteUser, RequestPermission

from pprint import pprint
from datetime import datetime


class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        
        model.init_session()
        c.site_readonly = config["site_readonly"]

        # IP Addr under boycott?
        if not c.site_readonly:
            start = model.Boycott.c.range_start
            stop = model.Boycott.c.range_stop
            expire = model.Boycott.c.expiration_date
            int_ip = h.get_client_int_ip()
            if model.Boycott.query.select(model.and_(start<=int_ip,
                                                     stop>=int_ip,
                                                     expire>datetime.utcnow())):
                c.site_readonly = True
                
        c.request = request

        # User messages that flash on the current page.  All in
        # Markdown format.  For message that flash on the next page,
        # useful for form response, use q_info() and q_warn().  You
        # can access them directly but h.m_info() and h.m_warn() is
        # recommended.
        c.m_info = []
        c.m_warn = []

        # full HTML content of the bars until we find something
        # smarter to store
        c.sidebars = []

        # for introspectinon and tabs highliting
        c.routes_dict = request.environ['pylons.routes_dict']

        # mostly for page footer
        c.version = __version__
        c.copyright_years = config["copyright_years"]
        c.copyright_owner = config["copyright_owner"]
        c.copyright_owner_email = config["copyright_owner_email"]

        # Level 1 navigation, small and not that important.
        # List of (lable, controller, action)
        c.nav1_actions = [
            ]

        if authorized(RemoteUser()):
            # should always be at the end
            c.nav1_actions.append(("Logout", "/visitor", "logout"))
        else:
            # TODO: just login and keep the current page
            c.nav1_actions.append(("Login", "/visitor", "login"))


        # Level 2 navigation, large and important.
        c.nav2_actions = [
            ("Home", "/wiki", "index"),
            ("About", "/wiki", "about"), 
            ("Contact", "/home", "contact"),
            ("Recent changes", "/wiki", "recent_changes"),
            ("Random", "/wiki", "random_page"),
            ]

        if h.has_rank("thaumaturge"):
            c.nav2_actions.append(("Abuse log", "/admin", "abuse_log"))
        
        # Level 3: page specific stuff that chages all the time
        c.nav3_actions = []
        
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            # you need to commit explicitly before this point or you
            # lose
            model.reclaim_session()

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
