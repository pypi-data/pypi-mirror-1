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


""" Utility functions for drawing and visualization of directed
acyclic graphs (DAG). """

# Technique heavily inspired by the graphlog.py Mercurial extention.
# There is no shared code, this is a re-implementation.

from pprint import pprint
from heapq import *
from collections import deque
import datetime
from ancestor import ancestor

import gazest.lib.helpers as h
import os


# Example dag from Mercurial's revlog 4658 to 4676; the 46 prefix is
# striped
ex1 = {76: [74, 75],
       75: [67],
       74: [73],
       73: [71, 72],
       72: [59],
       71: [68],
       68: [67],
       67: [61],
       61: [59],
       59: [58]
       }
ex1_h = 76


class FakeRev:
    """ Simulate an Alchemy RevNode object """
    def __init__(self, dag_h, id):
        self.dag_h = dag_h
        self.id = id
        self.creat_date = datetime.datetime.now() + datetime.timedelta(id*5)
        self.comment = "Fake rev with id '%s'" % id
        self.user = None
        self.creat_ip = "127.0.0.1"

    def parents(self):
        return [FakeRev(self.dag_h, id)
                for id in self.dag_h.get(self.id, [])]


class VizNode:
    def __init__(self, id, delegate_id=None, original_p=False):
        self.id = id
        self.delegate_id = delegate_id
        self.original_p = original_p


class VizDag:
    """ Minimal DAG representation.

    Nodes can be any hashable objects.  Given our particular usage,
    this implementation often assume a rooted DAG."""

    def __init__(self):
        # {node:[parent_1, parent_2]}
        self.map = {}
        self._nodes = set()

    def arc(self, source, dest):
        if not self.map.get(source):
            self.map[source] = set()
        self.map[source].add(dest)

    def nodes(self):
        return self._nodes

    def find_nodes(self, root):
        seen = set([root])
        nodes = deque([root])

        while nodes:
            node = nodes.popleft()
            for parent in self.parents(node):
                if not parent in seen:
                    nodes.append(parent)
                    seen.add(parent)
        return seen

    def parents(self, node):
        return self.map.get(node, set())
        
    def from_dict(self, dag_h, root):
        """ Init the VizDag from a dict in the same format as self.map."""
        self.map = dag_h
        self._nodes = self.find_nodes(root)

    def from_walk(self, root, parents_func):
        """ Init the VizDag by walking another DAG.

        The root should be hashable and parents_func should return an
        iterable container of hashable objects."""
        self.map = {}
        seen = set([root])
        nodes = deque([root])

        while nodes:
            node = nodes.popleft()
            for parent in parents_func(node):
                if parent not in seen:
                    nodes.append(parent)
                    seen.add(parent)
                self.arc(node, parent)
        self._nodes = seen

    def render_dot(self, outfile, root=None):
        """ Render a pretty PNG into outfile.

        Don't expect the full dag is you don't supply root because we
        have to pick an arbitrary node."""

        STUB = "digraph {%s}"
        CMD = "dot -T png > %s"

        if root is None:
            root=self.map.keys()[0]

        arcs = []
        seen = set([root])
        nodes = deque([root])

        while nodes:
            node = nodes.popleft()

            for parent in self.parents(node):
                arcs.append('"%s" -> "%s";' % (node, parent))

                if not parent in seen:
                    nodes.append(parent)
                    seen.add(parent)
        os.popen(CMD % outfile, "w").write(STUB % "\n".join(arcs))


def layout(root_rev):
    """ Take a rev dag and turn it in to a viz dag.

    The layout include the invisible anchor nodes to produce a
    vertical layout similar to qgit, gitk, or hgk."""

    # massage the revision graph
    nodes_h = {root_rev.id:root_rev}
    def parents(node_id):
        revs = nodes_h[node_id].parents()
        for rev in revs:
            nodes_h[rev.id] = rev
        return [rev.id for rev in revs]
    
    dag = VizDag()
    dag.from_walk(root_rev.id, parents)

    revs = sorted(dag.nodes(),
                  key=lambda id: nodes_h[id].creat_date,
                  reverse=True)

    # layout proper
    vizdag = VizDag()
    levels = []
    prev_level = []


    next_id = [-1]
    def new_node(delegate_id):
        node = VizNode(next_id[0], delegate_id, False)
        next_id[0] -= 1
        return node

    # one original node per new dag level
    for rev_id in revs:
        node = VizNode(rev_id, rev_id, True)
        linked = False
        cur_level = []
        
        # project a level
        for prev_node in prev_level:
            if rev_id in dag.parents(prev_node.delegate_id):
                # leads to a node with an arc on cur_node
                vizdag.arc(prev_node.id, rev_id)
                if not linked:
                    cur_level.append(node)
                linked = True
            else:
                cur_level.append(new_node(prev_node.delegate_id))
                vizdag.arc(prev_node.id, cur_level[-1].id)

            # branch as soon as we can
            # TODO: handle more than two children
            if prev_node.original_p and len(dag.parents(prev_node.id)) > 1:
                cur_level.append(new_node(prev_node.delegate_id))
                vizdag.arc(prev_node.id, cur_level[-1].id)
                
        if not linked:
            # This is a new root
            cur_level.append(node)
            
        levels.append([nodes_h[rev_id], cur_level])
        prev_level = cur_level
            
    return vizdag, levels


def arcval(top, bot):
    """ Return the arc value bit top link top to bot.  Some middle
    sections might be needed between then.  See the dagimage
    controller for details. """
    offset = max(min(bot-top, 1), -1) + 1
    val = 2**offset
    return val


def longarc(top, bot):
    """ Return true if top is too far from bot to be linked by a one
    level 45 degree or vertical arc. """
    return abs(bot-top) > 1


def longarc_len(top, bot):
    if longarc(top, bot):
        return abs(bot-top) - 1
    return 0


def node_img(top=1, bottom=1):
    # TODO: factor out the size
    url = h.url_for(controller="/dagimage",
                    action="node",
                    top=top,
                    bottom=bottom)
    return '<img width="24" height="24" src="%s" />' % url


def arc_img(top, mid, bottom):
    # TODO: factor out the size
    url = h.url_for(controller="/dagimage",
                    action="arc",
                    top=top,
                    mid=mid,
                    bottom=bottom)
    if top or mid or bottom:
        return '<img width="24" height="24" src="%s" />' % url
    else:
        return ''


def get_lca(a, b):
    """ Return the youngest common parent of a and b. """
    # just a wrapper over the Mercurial implementation

    rev_h = {a.id:a, b.id:b}
    def parents(rev_id):
        p_revs = rev_h[rev_id].parents()
        for rev in p_revs:
            rev_h[rev.id] = rev
        return [r.id for r in p_revs]
    lca_id = ancestor(a.id, b.id, parents)
    return rev_h[lca_id]


def html_layout(root_rev):
    dag, levels = layout(root_rev)
    nb_cols = max([len(lv[1]) for lv in levels]) 

    rows = []
    pre_nodes = []

    def new_block():
        # a matrix of arc values with one row for top, mid, and bot sections
        return [[0 for i in range(nb_cols)]
                for j in range(3)]

    # each level is rendered on two rows: one for arcs and one for
    # nodes
    for rev, nodes in levels:
        arcvals = new_block()
        a_row = []        
        n_row = []
        for j, pre_node in enumerate(pre_nodes):
            hori_segs = 0
            for i, near_node in enumerate(nodes):
                if hori_segs:
                    arcvals[1][i]|=1
                    hori_segs -= 1

                if near_node.id in dag.parents(pre_node.id):
                    arcvals[0][j]|=arcval(j, i)
                    hori_segs = max(hori_segs, longarc_len(j, i))

        for i, node in enumerate(nodes):
            hori_segs = 0
            for j, pre_node in enumerate(pre_nodes):
                if hori_segs:
                    arcvals[1][j]|=1
                    hori_segs -= 1

                if node.id in dag.parents(pre_node.id):
                    arcvals[2][i]|=arcval(j, i)
                    hori_segs = max(hori_segs, longarc_len(j, i))
            
            if node.original_p:
                n_row.append(node_img(root_rev.id==rev.id and "0" or "1",
                                      dag.parents(rev.id) and "1" or "0"))
            else:
                n_row.append(arc_img(2, 0, 2))

        # pad
        while len(n_row) < nb_cols:
            n_row.append("")

        a_row = [arc_img(arcvals[0][i], arcvals[1][i], arcvals[2][i])
                 for i in range(nb_cols)]
        
        rows.append([rev, a_row, n_row])
        pre_nodes = nodes
    return rows


if __name__ == "__main__":
    dag, levels = layout(FakeRev(ex1, ex1_h))
    dag.render_dot("/tmp/layout.png", ex1_h)

    def lca(a, b):
        print "LCA of %s and %s is %s" % (a, b,
                                          get_lca(FakeRev(ex1, a),
                                                  FakeRev(ex1, b)).id)
    lca(75, 76)
    lca(76, 75)
    lca(74, 75)
    lca(75, 75)
    lca(71, 72)
    
