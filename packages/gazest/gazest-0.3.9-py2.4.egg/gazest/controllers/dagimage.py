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

log = logging.getLogger(__name__)

import Image
from ImageDraw import Draw
from StringIO import StringIO

# TODO: caching
# see http://wiki.pylonshq.com/display/pylonsdocs/Caching+in+Templates+and+Controllers

class DagimageController(BaseController):

    def arc(self, top, mid, bottom):
        """ Arcs top and bottom sections are ORable bit fields:
          1: lower node is left
          2: vertical
          4: lower node is right
        Middle section is boolean."""

        col = (111, 121, 125)
        top, mid, bottom = map(int, [top, mid, bottom])
        response.headers['Content-Type'] = 'image/png'
        img = Image.new("RGB", (24, 24), color=(255,255,255))
        draw = Draw(img)

        # FIXME: A strange bug: PIL drops the last pixel of every
        # lines.  The current fix is to draw lines with a back and
        # forth stroke.  Don't get me wrong, this is ugly and it must
        # be fixed.
        for i in range(3):
            mask = 2**i
            if mask & top:
                draw.line(((12, 0), (12*i, 12)),
                          fill=col)
                draw.line(((12*i, 12), (12, 0)),
                          fill=col)
                
            if mask & bottom:
                draw.line(((12, 24), (12*(2-i), 12)),
                          fill=col)
                draw.line(((12*(2-i), 12), (12, 24)),
                          fill=col)
        if mid:
            draw.line(((0, 12), (24, 12)),
                      fill=col)

        sio = StringIO()
        img.save(sio, "PNG")
        
        return sio.getvalue()


    def node(self, top, bottom):
        col = (111, 121, 125)
        top, bottom = map(int, [top, bottom])
        response.headers['Content-Type'] = 'image/png'
        img = Image.new("RGB", (24, 24), color=(255,255,255))
        draw = Draw(img)

        draw.rectangle(((6, 6), (18, 18)),
                       fill=col)

        if top:
            draw.line(((12, 0), (12, 12)),
                      fill=col)

        if bottom:
            draw.line(((12, 12), (12, 24)),
                      fill=col)


        sio = StringIO()
        img.save(sio, "PNG")
        
        return sio.getvalue()
