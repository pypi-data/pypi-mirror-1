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

import logging

from gazest.lib.base import *
from pprint import pprint
from paste.deploy.converters import asbool

log = logging.getLogger(__name__)

class RobotsController(BaseController):
    def index(self):
        # TODO: include sitemap
        response.headers['Content-Type'] = 'text/plain'
        if asbool(config["staging"]):
            return "User-agent: * \nDisallow: /\n"
        else:
            return render("/robots.mako")
