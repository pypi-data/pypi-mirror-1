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


# A WikiPage is a mutable context used by macros for the rendering.
# It holds meta information about the page and it's by modifying it
# that macros can achieve non-local rendering, like addition of a
# side-bar or a footer.  All locally rendered macros should not modify
# it.

from gazest.lib import wiki_util
from markdown import markdown

class WikiPage:
    def __init__(self, slug):
        self.slug = slug
        self.title = wiki_util.get_page(slug)

        # default renderer is markdown but this is easy to override
        self.html_renderer = markdown

        # TODO: Implement the other renderers with decent fallback
        # rules.  As an example, if there is no PDF renderer but there
        # is a Docbook one, we should use db2pdf instead "printing"
        # the HTML to PDF with KHTML.

        # Callables called in chain on the body after the renderer but
        # before place holders are expanded.
        self.html_post_render_processors = []
        
        # Callables called in chain on the body after the place
        # holders are expanded.
        self.html_post_expand_processors = []

        # It's still not clear if sidebars should be HTML fragments or
        # something more detached from presentation.
        self.sidebars = []
        
