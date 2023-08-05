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

""" This module is mostly there to avoid circular import in the model. """

from pylons import request, c, session, config
import urllib2
import iplib

from datetime import timedelta

def get_client_ip():
    try:
        if config["nb_site_proxy"] == 0:
            return request.environ['REMOTE_ADDR']

        addr_lst = request.environ.get('HTTP_X_FORWARDED_FOR',
                                       request.environ['REMOTE_ADDR'])
        
        # This is not the client, it's the nth proxy beyond apache
        # (usually the 1st)
        return addr_lst.split(",")[-config["nb_site_proxy"]].strip()
    except KeyError:
        # probably in the shell
        return '127.0.0.1'
    except TypeError:
        # request is not bound
        return '127.0.0.1'


def get_client_int_ip():
    return int(iplib.convert(get_client_ip(), iplib.IP_DEC))


def site_base():
    return config["global_conf"]["site_base"]


def site_name():
    return config["global_conf"]["site_name"]


def taguri(date, namespace, id=None):
    """ Return a valid unique URI that is good for Atom feeds """
    domain = urllib2.urlparse.urlparse(site_base())[1].split(":")[0]
    datestr = date.date().isoformat()
    
    if id:
        return "tag:%s,%s:%s-%s" % (domain, datestr, namespace, id)
    else:
        return "tag:%s,%s:%s" % (domain, datestr, namespace)


def parse_timedelta(val):
    val = val.strip()
    if not val:
        return timedelta()
    
    days = 0
    if val.endswith("d"):
        days = float(val[:-1])
        
    secs = 0
    if val.endswith("h"):
        secs = float(val[:-1]) * 3600
    elif val.endswith("m"):
        secs = float(val[:-1]) * 60
    elif val.endswith("s"):
        secs = float(val[:-1])
    else:
        secs = float(val[:-1])
        
    return timedelta(days=days, seconds=secs)


