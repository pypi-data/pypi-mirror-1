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

from authkit.pylons_adaptors import authorize
from gazest.lib.auth_util import HasRank
from gazest.lib.formutil import CIDRValidator
from datetime import datetime, timedelta

import formencode

log = logging.getLogger(__name__)


class BoycottForm(formencode.Schema):
    allow_extra_fields = True
    range_cidr = CIDRValidator()
    nb_days = formencode.validators.Number()
    reason = formencode.validators.UnicodeString(strip=True)


class AdminController(BaseController):
    def __before__(self, action, **kw):
        c.noindex = True

    @authorize(HasRank("thaumaturge"))
    def abuse_log(self):
        # TODO: This is a pretty minimal report.  We should improve
        # it.
        date_col = model.AbuseReport.c.creat_date
        reports = model.AbuseReport.select(order_by=date_col,
                                           limit=200)
        # group by rev
        abuse_h = {}
        revs = []
        for report in reports:
            rev_id = report.rev.id
            if not abuse_h.has_key(rev_id):
                abuse_h[rev_id] = 0
                revs.append(report.rev)
            abuse_h[rev_id] += 1
        revs.sort(lambda a, b: a.creat_date < b.creat_date)
        c.rev_rep_pairs = [(r, abuse_h[r.id]) for r in revs]
        
        return render("/wiki_abuse_log.mako")


    @authorize(HasRank("thaumaturge"))
    def boycott_form(self, addr=None):
        if addr:
            c.range_cidr = "%s/32" % addr

        # TODO: we should check for previous offenses and double the
        # duration
        c.nb_days = 2

        return render("/admin_boycott_form.mako")


    @authorize(HasRank("thaumaturge"))
    @validate(schema=BoycottForm(), form='boycott_form')
    def boycott_action(self):
        # TODO: abort if there is already an active ban on this range
        
        cidr = self.form_result["range_cidr"]
        days = self.form_result["nb_days"]
        now = datetime.utcnow()
        delay = timedelta(days=days)
        boycott = model.Boycott(reason=self.form_result["reason"],
                                range_cidr=str(cidr),
                                range_start=int(cidr.first_ip.get_dec()),
                                range_stop=int(cidr.last_ip.get_dec()),
                                expiration_date=now+delay,
                                instigator=h.get_remote_user())
        model.ctx.current.flush()
        h.q_info("Boycotting %s IP addresses for %s days" % (len(cidr), days))
        return h.redirect_to(action="abuse_log")
