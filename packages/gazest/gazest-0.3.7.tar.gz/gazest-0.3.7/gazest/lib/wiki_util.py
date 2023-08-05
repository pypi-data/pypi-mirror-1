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


""" Utility function for the Wiki.  This module is mostly there to
prevent circular include between markup.py and wiki_macros.py ."""

import urllib


# this will be populated by environment.py
extra_macros = {}


def get_namespace(page_slug):
    # We could receive a page slug or a namespace slug here.  Is there
    # a way to tell one from the other?  Of course not since we want
    # all pages to potentially act as namespaces.  The only solution
    # is to assume a page slug.
    levels = page_slug.strip("/").split("/")
    if levels:
        return "/".join(levels[:-1])
    else:
        return ""


def get_page(page_slug):
    # We could receive a page slug or a namespace slug here
    # is there a way to tell one from the other?
    # of course not, we want all pages to potentially act as namespaces.
    # The only solution is to assume a page slug
    levels = page_slug.strip("/").split("/")
    return levels[-1]


def normalize_page(page):
    # At the moment, all pages must start with a capital letter.  This
    # isn't completly right but it prevent us from having to reserve
    # words for actions.
    return urllib.quote(page.strip().encode("UTF-8").capitalize())


def normalize_slug(slug):
    return "/".join(map(normalize_page,
                        slug.strip("/").split("/")))

    
