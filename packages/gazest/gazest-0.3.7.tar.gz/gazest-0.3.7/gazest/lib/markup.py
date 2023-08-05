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



from pprint import pprint
from gazest.lib.wikipage import WikiPage
from gazest.lib.wiki_util import *
from pylons import config

import gazest.lib.helpers as h
import re
import sha
import wiki_macros
import logging

log = logging.getLogger(__name__)

# We are liberal on what we accept; anything can be rendered and will
# produce a result.  It's not to say that we won't spot erroneous
# markup and won't signal it to our user.

# Our strategy is simple: formating is handled by a plugable HTML
# generator (the default is markdown) and wiki-linking by ourself.  We
# fist replace wiki markup by place holders, tell the HTML renderer to
# expand the presentation then put the stubs expansions back into place.

# Unlike MediaWiki's, our wiki markup is not context dependant.

# note that this is _not_ multiline
WIKI_LINK_PAT = re.compile(r"(\[\[.*?\]\])", re.UNICODE)
WIKI_LINK_INFO_PAT = re.compile(r"\[\[(.*?)(?:\|(.*?))?\]\]", re.UNICODE)

PLACEHOLDER_PAT = re.compile(r"(\[\[\[place_holder .+?\]\]\])")
PLACEHOLDER_INFO_PAT = re.compile(r"\[\[\[place_holder (.+?)\]\]\]")

MACRO_PAT = re.compile(r"({{.+?}})")
MACRO_INFO_PAT = re.compile(r"{{(.+?)(?:\s+(.+?))?}}")

# TODO: This renderer is slow but there is much place for improvement.

def make_id(tag):
    return sha.new(tag.encode("utf-8")).hexdigest()


def expand_wiki_link(tag):
    # TODO: expand namespaces
    page, label = WIKI_LINK_INFO_PAT.search(tag).groups()
    slug = normalize_page(page)
    url = h.url_for(controller="/wiki",
                    action="view",
                    slug=slug)
    return '<a href="%s">%s</a>' % (url, label or page)
    

def make_placeholder(tag, stubs_h, expand_fun):
    """ Returns a placeholder macro tag for a non context specific tag
    and add it to stubs_h."""
    stub_id  = make_id(tag)
    stub = "[[[place_holder %s]]]" % stub_id
    stubs_h[stub_id] = expand_fun(tag)
    return stub


def expand_placeholder(tag, stubs_h):
    stub_id = PLACEHOLDER_INFO_PAT.search(tag).group(1)
    return stubs_h[stub_id]


def expand_macro(page, tag):
    name, args = MACRO_INFO_PAT.search(tag).groups()

    # What should we do with macros that we don't know?  The worst
    # option is to return the unrendered tag for all users to see.  We
    # just log the error and strip the offending markup.

    try:
        prefix, fname = name.rsplit(".", 1)
        module = extra_macros[prefix]
    except ValueError:
        fname = name
        module = wiki_macros
    except KeyError:
        log.debug("No macro package called '%s'" % prefix)
        return ""

    if fname.startswith("_"):
        log.debug("Macros cannot be 'protected' functions."
                  " Requested name was: %s" % fname)
        return ""
    
    try:
        funct = getattr(module, fname)
    except AttributeError:
        log.debug("Invalid wiki macro: %s" % name)
        return ""

    return funct(page, args)


def replace_page_tags(body, pat, rep_fun):
    """ replace the tags in body matched by the compiled regexp pat
    what rep_fun(tag) returns."""
    frags = []
    prev_stop = 0
    for match in pat.finditer(body):
        frags.append(body[prev_stop:match.start()])
        prev_stop = match.end()
        tag = match.group()
        stub = rep_fun(tag)
        frags.append(stub)
    frags.append(body[prev_stop:])
    return "".join(frags)
    

def render_page(body, slug=None):
    # Markup like '[[[place_holder id]]]' is expanded after html
    # generation.
    page = WikiPage(slug)
    if config["wiki_header"]:
        body = "%s\n%s" % (config["wiki_header"], body)
    if config["wiki_footer"]:
        body = "%s\n%s" % (body, config["wiki_footer"])

    stubs_h = {}
    def make_rep_fun(expand_fun):
        return lambda tag:make_placeholder(tag, stubs_h, expand_fun)

    # 1st pass: wiki links
    body = replace_page_tags(body,
                             WIKI_LINK_PAT,
                             make_rep_fun(expand_wiki_link))
    
    # 2nd pass: functions and macros
    body = replace_page_tags(body,
                             MACRO_PAT,
                             make_rep_fun(lambda tag:expand_macro(page, tag)))

    # 3rd pass: HTML generation
    body = page.html_renderer(body)
    for processor in page.html_post_render_processors:
        body = processor(body)

    # 4th pass: expand place holders
    body = replace_page_tags(body,
                             PLACEHOLDER_PAT,
                             lambda tag:expand_placeholder(tag, stubs_h))

    for processor in page.html_post_expand_processors:
        body = processor(body)

    return page, body
