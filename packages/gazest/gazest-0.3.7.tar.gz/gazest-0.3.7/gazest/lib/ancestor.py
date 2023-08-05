#  ancestor.py - generic DAG ancestor algorithm for mercurial
 
#  Copyright 2006 Matt Mackall <mpm@selenic.com>

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

import heapq

def ancestor(a, b, pfunc):
    """
    return the least common ancestor of nodes a and b or None if there
    is no such ancestor.

    pfunc must return a list of parent vertices
    """

    if a == b:
        return a

    # find depth from root of all ancestors
    visit = [a, b]
    depth = {}
    while visit:
        vertex = visit[-1]
        pl = pfunc(vertex)
        if not pl:
            depth[vertex] = 0
            visit.pop()
        else:
            for p in pl:
                if p == a or p == b: # did we find a or b as a parent?
                    return p # we're done
                if p not in depth:
                    visit.append(p)
            if visit[-1] == vertex:
                depth[vertex] = min([depth[p] for p in pl]) - 1
                visit.pop()

    # traverse ancestors in order of decreasing distance from root
    def ancestors(vertex):
        h = [(depth[vertex], vertex)]
        seen = {}
        while h:
            d, n = heapq.heappop(h)
            if n not in seen:
                seen[n] = 1
                yield (d, n)
                for p in pfunc(n):
                    heapq.heappush(h, (depth[p], p))

    def generations(vertex):
        sg, s = None, {}
        for g, v in ancestors(vertex):
            if g != sg:
                if sg:
                    yield sg, s
                sg, s = g, {v:1}
            else:
                s[v] = 1
        yield sg, s

    x = generations(a)
    y = generations(b)
    gx = x.next()
    gy = y.next()

    # increment each ancestor list until it is closer to root than
    # the other, or they match
    try:
        while 1:
            if gx[0] == gy[0]:
                for v in gx[1]:
                    if v in gy[1]:
                        return v
                gy = y.next()
                gx = x.next()
            elif gx[0] > gy[0]:
                gy = y.next()
            else:
                gx = x.next()
    except StopIteration:
        return None
