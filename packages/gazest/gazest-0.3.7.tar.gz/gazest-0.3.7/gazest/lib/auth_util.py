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


from webhelpers import *
from authkit.permissions import NotAuthenticatedError, NotAuthorizedError
from authkit.permissions import RemoteUser, RequestPermission
from gazest.lib import helpers as h
from pylons.controllers.util import abort

class HasRank(RequestPermission):
    def __init__(self, rank):
        self.lvl = h.rank_lvl(rank)
        #self.error = NotAuthorizedError("Insufficient privileges")

    def check(self, app, environ, start_response):
        user = h.get_remote_user()
        if not user:
            raise NotAuthenticatedError('Not Authenticated')
        if user.rank >= self.lvl:
            return app(environ, start_response)
        else:
            msg = ("You need to be %s or"
                   " higher to see this page" % h.lvl_rank(self.lvl))
            abort(403,  msg)
