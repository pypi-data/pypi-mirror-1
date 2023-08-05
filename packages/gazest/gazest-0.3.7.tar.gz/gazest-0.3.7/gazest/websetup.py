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

"""Setup the gazest application"""
import logging

from paste.deploy import appconfig
from pylons import config

from gazest.config.environment import load_environment
import extra_data
from pkg_resources import resource_string

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup gazest here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    # bootstrap the DB
    from gazest import model
    from pylons.database import create_engine
    uri = conf['sqlalchemy.dburi']
    engine = create_engine(uri)
    model.meta.connect(engine)
    model.meta.create_all()

    # pre-insert stuff
    # at very least, we need a namespace with page stubs
    stub_rev = model.RevNode()
    resource_string(extra_data.__name__,
                    "default_not_found_page.txt")
    #stub_rev.body=open("extra_data/default_stub_page.txt").read()
    stub_rev.body=resource_string(extra_data.__name__,
                                  "default_stub_page.txt")

    not_found_rev = model.RevNode()
    #not_found_rev.body=open("extra_data/default_not_found_page.txt").read()
    not_found_rev.body=resource_string(extra_data.__name__,
                                       "default_not_found_page.txt")
    
    ns = model.Namespace(stub_rev=stub_rev,
                         not_found_rev=not_found_rev,
                         slug="",
                         wikiprefix="def",
                         name="default namespace",)
    
    model.ctx.current.flush()
    
