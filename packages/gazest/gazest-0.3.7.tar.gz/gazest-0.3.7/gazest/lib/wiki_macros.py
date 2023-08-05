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


# All those functions are called to perform rendering on a page.  The
# first argument is always a WikiPage instance.  The second argument
# is a non-parsed string or all arguments.  This might be parsed in
# the future.

import gazest.lib.helpers as h
from gazest.lib import wiki_util
import re


def duplicate(page, text):
    # useless example macro
    return "%s %s" % (text, text)


def edit_self(page, label):
    """ Return a link to edit the current page. """
    url = h.url_for(controller="/wiki",
                    action="edit_form",
                    slug=wiki_util.normalize_slug(page.slug))
    return '<a href="%s">%s</a>' % (url, label or "edit")

def title(page, title):
    """ Override the title infered from the slug. """
    page.title = title
    return ""


def rel_nofollow(page, arg):
    """ Mark all external links with ``rel="nofollow"`` """
    A_PAT = re.compile(r"(<a\s.*?>)", re.UNICODE | re.DOTALL)
    def rep(match):
        tag = match.group(0)
        if tag.find('nofollow') != -1:
            return tag
        else:
            return tag[:-1] + ' rel="nofollow">'
    def fix_tags(body):
        return re.sub(A_PAT, rep, body)
    page.html_post_render_processors.append(fix_tags)
    return ""
