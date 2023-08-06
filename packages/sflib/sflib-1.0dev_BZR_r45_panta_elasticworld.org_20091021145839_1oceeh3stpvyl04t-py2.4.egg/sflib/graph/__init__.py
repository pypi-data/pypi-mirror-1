#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
python-sflib graph library.

Author: Marco Pantaleoni
Copyright (C) 2007-2008 Marco Pantaleoni. All rights reserved.

Graph data structures.

>>> g = Graph()

>>> n_undershorts = Node("undershorts")

>>> n_pants = Node("pants")

>>> n_belt = Node("belt")

>>> n_shirt = Node("shirt")

>>> n_tie = Node("tie")

>>> n_jacket = Node("jacket")

>>> n_socks = Node("socks")

>>> n_shoes = Node("shoes")

>>> n_watch = Node("watch")

>>> g.AddEdgeNodes(n_pants, n_undershorts)

>>> g.AddEdgeNodes(n_belt, n_pants)

>>> g.AddEdgeNodes(n_jacket, n_belt)

>>> g.AddEdgeNodes(n_belt, n_shirt)

>>> g.AddEdgeNodes(n_tie, n_shirt)

>>> g.AddEdgeNodes(n_jacket, n_tie)

>>> g.AddEdgeNodes(n_shoes, n_socks)

>>> g.AddEdgeNodes(n_shoes, n_undershorts)

>>> g.AddEdgeNodes(n_shoes, n_pants)

>>> g.AddNode(n_watch)

>>> ts = TopologicalSort(g)

>>> ts.run()

>>> ts.sorted
[<Node shirt>, <Node watch>, <Node socks>, <Node undershorts>, <Node pants>, <Node shoes>, <Node belt>, <Node tie>, <Node jacket>]
"""

import unittest

class Node:
    """
    Graph node
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return u"%s" % (self.name)

    def __repr__(self):
        return u"<Node %s>" % self.name

    def __cmp__(self, other):
        if other == None:
            return -1
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name)

class Edge:
    """
    Graph edge
    """

    def __init__(self, src, dst, etype=None):
        self.src = src
        self.dst = dst
        self.etype = etype

    def __str__(self):
        if self.etype:
            return u"%s(%s -> %s)" % (self.etype, self.src, self.dst)
        return u"(%s -> %s)" % (self.src, self.dst)

    def __repr__(self):
        if self.etype:
            return u"<Edge %s %s -> %s>" % (self.etype, self.src, self.dst)
        return u"<Edge %s -> %s>" % (self.src, self.dst)

class Graph:
    """
    Unidirected Graph
    """

    def __init__(self):
        self.adj  = {}                  # adjacency matrix - indexed by vertex
        self.edge = {}                  # graph edges - indexed by vertex

    def GetVertices(self):
        """
        Get all the verices of the graph.
        """
        return self.adj.keys()

    def GetEdges(self):
        """
        Get all the edges of the graph.
        """
        edges = []
        vertices = self.GetVertices()
        for v1 in vertices:
            for v2 in self.adj[v1]:
                edges.append((v1, v2))
        return edges

    def GetAdjacencyList(self):
        return self.adj

    def GetAdjacencyMatrix(self):
        vertices = self.GetVertices()
        matrix = {}
        for v1 in vertices:
            matrix[v1] = {}
            for v2 in vertices:
                matrix[v1][v2] = False

        for v1 in vertices:
            for v2 in self.adj[v1]:
                matrix[v1][v2] = True

        return matrix

    def AddNode(self, node):
        if not node in self.adj:
            self.adj[node] = []
            self.edge[node] = {}

    def _has_edge(self, src, dst):
        if not src in self.edge:
            return False
        if not dst in self.edge[src]:
            return False
        return True

    def _add_edge(self, src, dst, edge):
        if not src in self.edge:
            self.edge[src] = {}
        if not dst in self.edge[src]:
            assert not dst in self.edge[src]
            self.edge[src][dst] = edge

    def _get_edge(self, src, dst):
        if not src in self.edge:
            return None
        if not dst in self.edge[src]:
            return None
        return self.edge[src][dst]

    def AddEdge(self, edge):
        src = edge.src
        dst = edge.dst
        self.AddNode(src)
        self.AddNode(dst)
        if dst not in self.adj[src]:
            self.adj[src].append(dst)
        self._add_edge(src, dst, edge)

    def AddEdgeNodes(self, src, dst, etype=None):
        edge = Edge(src, dst, etype)
        self.AddEdge(edge)

    def HasEdge(self, src, dst):
        return dst in self.adj[src]

    def GetEdge(self, src, dst):
        return _get_edge(src, dst)


    def String(self):
        import sys
        lines = []
        adj_keys = self.adj.keys()
        adj_keys = sorted(adj_keys, lambda a, b: cmp(a.name, b.name))
        for n in adj_keys:
            adj_s = ""
            for a in self.adj[n]:
                a_s = "%s" % a
                if adj_s != "":
                    adj_s = adj_s + " " + a_s
                else:
                    adj_s = a_s
            lines.append("%s -> %s" % (n, adj_s))
        return reduce(lambda x, y: x + '\n' + y, lines)

    def Print(self):
        print self.String()

    def __str__(self):
        return u"Graph"

class BFS:
    """
    BFS algorithm.
    """

    WHITE = 3
    GRAY  = 2
    BLACK = 1

    INFINITE = 10000000

    def __init__(self, graph, start):
        self.graph = graph
        self.start = start
        self.color = {}                 # WHITE, GRAY or BLACK
        self.d     = {}
        self.pi    = {}

    def run(self):
        from queues import Queue

        G = self.graph
        start = self.start
        vertices = G.GetVertices()
        for u in vertices:
            self.color[u] = BFS.WHITE
            self.d[u]     = BFS.INFINITE
            self.pi[u]    = None
        self.color[start] = BFS.GRAY
        self.d[start] = 0
        self.pi[start] = None
        Q = Queue()
        Q.Enqueue(start)
        while not Q.Empty():
            u = Q.Head()
            for v in G.adj[u]:
                if self.color[v] == BFS.WHITE:
                    self.color[v] = BFS.GRAY
                    self.d[v] = self.d[u] + 1
                    self.pi[v] = u
                    Q.Enqueue(v)
            Q.Dequeue()
            self.color[u] = BFS.BLACK

    def path(self, s, v):
        if v == s:
            return s
        else:
            if self.pi[v] == None:
                return None             # no path from s to v
            else:
                p1 = self.path(s, self.pi[v])
                p2 = v
                if p1 == None:
                    return None         # no path from s to v
                elif type(p1) == type(()):
                    p = p1 + (v,)
                else:
                    p = (p1, v)
                return p

class DFS:
    """
    DFS algorithm.
    """

    WHITE = 3
    GRAY  = 2
    BLACK = 1

    INFINITE = 10000000

    def __init__(self, graph, f_callback=None):
        self.graph = graph
        self.time  = 0                  # "clock"
        self.color = {}                 # WHITE, GRAY or BLACK
        self.d     = {}                 # discovering time
        self.f     = {}                 # finishing time
        self.pi    = {}

        self.f_callback = f_callback

    def run(self):
        G = self.graph

        vertices = G.GetVertices()
        for u in vertices:
            self.color[u] = DFS.WHITE
            self.d[u]     = DFS.INFINITE
            self.f[u]     = 0
            self.pi[u]    = None

        self.time = 0

        for u in vertices:
            if self.color[u] == DFS.WHITE:
                self.DFS_visit(u)

    def DFS_visit(self, u):
        self.color[u] = DFS.GRAY
        self.time += 1
        self.d[u] = self.time
        for v in self.graph.adj[u]:
            if self.color[v] == DFS.WHITE:
                self.pi[v] = u
                self.DFS_visit(v)
        self.color[u] = DFS.BLACK
        self.time += 1
        self.f[u] = self.time
        if self.f_callback:
            self.f_callback(u)

class TopologicalSort:
    """
    Topological sort algorithm
    """

    def __init__(self, graph):
        self.graph = graph
        self.dfs   = DFS(graph, f_callback = lambda u, s=self: s._store(u))
        self.sorted = []

    def run(self):
        self.dfs.run()
        #self.sorted.reverse()

    def _store(self, u):
        self.sorted.append(u)

class TestTopologicalSort(unittest.TestCase):
    def setUp(self):
        g = Graph()
        self.n_undershorts = Node("undershorts")
        self.n_pants = Node("pants")
        self.n_belt = Node("belt")
        self.n_shirt = Node("shirt")
        self.n_tie = Node("tie")
        self.n_jacket = Node("jacket")
        self.n_socks = Node("socks")
        self.n_shoes = Node("shoes")
        self.n_watch = Node("watch")
        g.AddEdgeNodes(self.n_pants, self.n_undershorts)
        g.AddEdgeNodes(self.n_belt, self.n_pants)
        g.AddEdgeNodes(self.n_jacket, self.n_belt)
        g.AddEdgeNodes(self.n_belt, self.n_shirt)
        g.AddEdgeNodes(self.n_tie, self.n_shirt)
        g.AddEdgeNodes(self.n_jacket, self.n_tie)
        g.AddEdgeNodes(self.n_shoes, self.n_socks)
        g.AddEdgeNodes(self.n_shoes, self.n_undershorts)
        g.AddEdgeNodes(self.n_shoes, self.n_pants)
        g.AddNode(self.n_watch)
        self.g = g

    def test_string(self):
        self.assertEqual(self.g.String(), u'belt -> pants shirt\njacket -> belt tie\npants -> undershorts\nshirt -> \nshoes -> socks undershorts pants\nsocks -> \ntie -> shirt\nundershorts -> \nwatch -> ')
        #self.assertEqual(self.g.String(), u'belt -> jacket\njacket -> \npants -> belt shoes\nshirt -> belt tie\nshoes -> \nsocks -> shoes\ntie -> jacket\nundershorts -> pants shoes\nwatch -> ')

    def test_tsort(self):
        ts = TopologicalSort(self.g)
        ts.run()
        tsorted = ts.sorted
        self.assert_(tsorted.index(self.n_socks) < tsorted.index(self.n_shoes))
        self.assert_(tsorted.index(self.n_undershorts) < tsorted.index(self.n_pants))
        self.assert_(tsorted.index(self.n_undershorts) < tsorted.index(self.n_shoes))
        self.assert_(tsorted.index(self.n_pants) < tsorted.index(self.n_belt))
        self.assert_(tsorted.index(self.n_pants) < tsorted.index(self.n_shoes))
        self.assert_(tsorted.index(self.n_shirt) < tsorted.index(self.n_belt))
        self.assert_(tsorted.index(self.n_shirt) < tsorted.index(self.n_tie))
        self.assert_(tsorted.index(self.n_tie) < tsorted.index(self.n_jacket))

def _test():
    unittest.main()
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
