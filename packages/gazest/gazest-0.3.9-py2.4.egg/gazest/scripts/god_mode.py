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


""" Command line script to turn a user into a site admin """

import sys

from paste.deploy import appconfig
from pylons import config
from gazest.config.environment import load_environment

from optparse import OptionParser
from gazest import version
import os

engine = None

DEF_RANK = "thaumaturge"

def load(filename):

    conf = appconfig('config:' + os.path.abspath(filename))
    load_environment(conf.global_conf, conf.local_conf)
    global model
    from gazest import model


def ascend(username, rank=DEF_RANK):
    import gazest.lib.helpers as h

    user = model.User.query.filter(model.User.username==username).one()
    user.rank = h.rank_lvl(rank)
    # TODO: send a gazmail telling how nice it is to be a super user


def main():
    parser = OptionParser(usage = "%prog CONFIG_FILE USER1 [USER2 ...]")
    
    parser.add_option("-V", "--version",
                      action="store_true", dest="version", default=False,
                      help="print software version and exit")

    parser.add_option("-r", "--rank",
                      dest="rank", default=DEF_RANK,
                      help="set user rank to RANK [default: %s]" % DEF_RANK)

    parser.add_option("-l", "--list-ranks",
                      action="store_true", dest="list_ranks", default=False,
                      help="print rank names and exit")

    parser.add_option("-L", "--list-users",
                      action="store_true", dest="list_users", default=False,
                      help="print all user names and exit")


    (opts, args) = parser.parse_args()
    if opts.version:
        print "gazest-god-mode %s" % version
        sys.exit(0)

    if opts.list_ranks:
        print "User ranks: %s" % ", ".join(model.USER_RANKS)
        sys.exit(0)

    if len(args) < 1:
        parser.error("Missing config file")

    load(args[0])

    if opts.list_users:
        users = model.User.select()
        for user in users:
            print user.username
        if not users:
            print "No users"
        sys.exit(0)

    if len(args) < 2:
        parser.error("No user specified")

    for usr in args[1:]:
        ascend(usr, opts.rank)
    model.db_sess.commit()


if __name__ == "__main__":
    main()
    
