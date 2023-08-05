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

"""Pylons environment configuration"""
import os

from pylons import config

import gazest.lib.app_globals as app_globals
import gazest.lib.helpers
from gazest.lib import helpers

from gazest.lib.wiki_util import extra_macros
from gazest.config.routing import make_map
from pprint import pprint
from pkg_resources import iter_entry_points


def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=[app_conf["extra_statics"],
                               os.path.join(root, 'public')],
                 templates=[app_conf["extra_templates"],
                            os.path.join(root, 'templates'),])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='gazest',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = gazest.lib.helpers

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)

    # FIXME: hack until pylons has config in the template namespaces
    config['pylons.g'].config = config

    delay = helpers.parse_timedelta(config["wiki_indexing_delay"])
    config['pylons.g'].wiki_indexing_delay = delay
    
    # load wiki_macros
    for ep in iter_entry_points('gazest.wiki_macros'):
        extra_macros[ep.name] = ep.load()
