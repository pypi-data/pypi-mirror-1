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


from pylons import request, c, session, config

from openid.store.filestore import FileOpenIDStore
from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure

import os

def openid_store():
    cache = config["app_conf"]["cache_dir"]
    storepath = os.path.join(cache, "openid_store.db")
    return FileOpenIDStore(storepath)


def openid_consumer():
    return consumer.Consumer(session, openid_store())


try:
    # python-openid 2.x
    from openid import urinorm
    def normalizeURI(uri):
        return urinorm.urinorm(uri)

except ImportError:
    # python-openid 1.2
    from openid import oidutil
    def normalizeURI(uri):
        return oidutil.normalizeUrl(uri)

