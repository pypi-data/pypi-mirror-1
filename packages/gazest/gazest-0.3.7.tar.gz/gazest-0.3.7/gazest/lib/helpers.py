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

"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *
from pylons.controllers.util  import log
from pylons.i18n import get_lang, set_lang
from pylons import request, c, session, config
from pylons.templating import render
import smtplib
from request_util import *
from difflib import Differ, HtmlDiff
import difflib
from datetime import timedelta

#from formencode import Schema, validators, All

from gazest import model

import os            

def set_auth_cookie(username):
    # This should be Unicode transparent but the current AuthKit version is
    # buggy
    # TODO: kick the manual encoding
    request.environ['paste.auth_tkt.set_user'](username.encode("utf-8"))
    #request.environ['paste.auth_tkt.set_user'](username)

            
def render_email(template):
    """Send a mako rendered mail.
    
    All params must be plugged in to c by the caller.  The important one is
    
    c.to_addr

    Optional ones are

    c.from_addr 
    c.subject"""

    conf = config["global_conf"]

    if not c.from_addr:
        c.from_addr = conf["system_email_from"]
        
    # template must render the envelope headers
    msg = render(template)

    server = smtplib.SMTP(conf["smtp_server"])
    server.sendmail(c.from_addr, c.to_addr, msg)
    server.quit()


def get_remote_user():
    try:
        username = request.environ["REMOTE_USER"]
    except KeyError:
        return None
    return model.User.selectfirst_by(username=username, status="active")


def pretty_date(dt):
    """Return a nice date time representation.  
    
    dt sould be a date or a datetime"""
    return "%s %s" % (dt.date(), dt.strftime("%X"))


def pretty_bool(val):
    """Return a representation of booleans suitable for the Web."""
    # FIXME: we need a better icon for no, untill then, no icon is better
    if not val:
        return "no"

    if val:
        alt = "yes"
        img = "cr22-action-button_ok.png"
    else:
        alt = "no"
        img = "cr22-action-button_cancel.png"
    return '<img src="/img/%s" alt="%s" width="22" height="22" />' % (
        img,
        alt)


def fq_url_for(*args, **kwargs):
    return site_base() + url_for(*args, **kwargs)


def q_info(msg):
    """Schedule a message for flashing on the next visited page."""
    session['m_info'] = session.get('m_info',[]) + [msg]
    session.save()


def q_warn(msg):
    """Schedule a warning for flashing on the next visited page."""
    session['m_warn'] = session.get('m_warn',[]) + [msg]
    session.save()


def m_info(msg):
    """Add a message for flashing on visited page."""
    c.m_info.append(msg)


def m_warn(msg):
    """Add a warning for flashing on visited page."""
    c.m_warn.append(msg)


def diff_highlight(from_rev, to_rev):
    # TODO: I spent some time reading the source code of other
    # Python wiki looking for reusable diff rendering.  I was sure
    # that it had been a complete waste of time when I discovered
    # that the Python standard lib included an HTML renderer for
    # diffs.  But seeing the ugly result, I now understand why
    # other wikis went the hard way to make pretty outputs.  The
    # rendered from Moin is quite self-contained in
    # wikiutil.linediff(), that's what we should use.  It might
    # also be possible to rescue the current renderer by fixing
    # line wrapping.
    #                                                  -- YGingras

    from_url = url_for(action="past_revision", rev_id=from_rev.id)
    fromdesc='<a href="%s">old version</a>' % from_url

    if to_rev.id:
        to_url = url_for(action="past_revision", rev_id=to_rev.id)
        todesc='<a href="%s">new version</a>' % to_url
    else:
        todesc='new version'
    
    differ = HtmlDiff(wrapcolumn=46)
    diff = differ.make_table(from_rev.body.encode("utf-8").split("\n"),
                             to_rev.body.encode("utf-8").split("\n"),
                             context=True,
                             numlines=2,
                             fromdesc=fromdesc,
                             todesc=todesc)
    return unicode(diff, "utf-8")


def diff_stats(from_rev, to_rev):
    differ = Differ()
    diff = differ.compare(from_rev.body.split("\n"),
                          to_rev.body.split("\n"))
    gain = 0
    lost = 0
    for l in diff:
        if l.startswith("+"):
            gain += 1
        elif l.startswith("-"):
            lost += 1
    return gain, lost


def diff_unified(from_rev, to_rev):
    from_user = from_rev.user and from_rev.user.username or from_rev.creat_ip
    to_user = to_rev.user and to_rev.user.username or to_rev.creat_ip

    diff = difflib.unified_diff(from_rev.body.split("\n"),
                                to_rev.body.split("\n"),
                                fromfile='old verion by %s' % from_user,
                                tofile='new verion by %s' % to_user,
                                fromfiledate=from_rev.creat_date,
                                tofiledate=to_rev.creat_date,
                                n=3,
                                lineterm='')

    return "\n".join(diff)


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


def rank_lvl(rank):
    """ Return a rank numeric id.  Rank can be a rank number or a rank
    name. """
    try:
        lvl = int(rank)
    except ValueError:
        lvl = model.RANK_LVLS[rank]
    return lvl


def lvl_rank(lvl):
    """ Return a rank name. """
    if lvl in model.USER_RANKS:
        return lvl
    return model.USER_RANKS[lvl]


def has_rank(rank):
    """ Return true if the user is logged has at least the given rank."""
    user = get_remote_user()
    if not user:
        return False
    if user.rank >= rank_lvl(rank):
        return True
    return False
