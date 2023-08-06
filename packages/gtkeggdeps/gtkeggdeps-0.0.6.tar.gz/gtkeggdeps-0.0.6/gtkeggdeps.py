#!/usr/bin/env python

import sys
import os
import glob
import optparse
import gtk
import tl.eggdeps.graph


class ExtraDiscerningGraph(tl.eggdeps.graph.Graph):
    """Dependency graph that remembers extras.

    tl.eggdeps.graph.Graph discards the extras components from requirement
    specifications, so if package A requires package X, and package B requires
    package X with some extras, the graph nodes for A and B will be identical.

    (It remembers information going in the other direction, e.g. if package X
    requires package M, but if you want package X with an extra, it will also
    require package N, then graph['X'] will be dict(M=set(), N=set('extra'))).

    This doesn't suit me, so I override names() to create fake nodes of the
    form 'project_name[extra]'.  As a result, if a package B requres package X
    with [extra1, extra2], you'll see three names in the specs list::

        graph['B'].deps == {'X': set(),
                            'X[extra1]': set(),
                            'X[extra2]': set()}

    Since deps is also used for graph traversal, I override __getitem__()
    so that graph['X[extra1'] is the same thing as graph['X'].  It is perhaps
    not very nice, but it seems to work.
    """

    def __getitem__(self, name):
        if '[' in name:
            name = name.split('[', 1)[0]
        return tl.eggdeps.graph.Graph.__getitem__(self, name)

    def names(self, specs):
        names = set()
        for s in specs:
            if self.show(s.project_name):
                names.add(s.project_name)
                for extra in s.extras:
                    names.add(s.project_name + '[' + extra + ']')
        return names


class MyTreeModel(gtk.GenericTreeModel):
    """Represent a graph as a tree with duplicated nodes (and subtrees).

    Handles cycles correctly.
    """

    def __init__(self, graph, reverse=False):
        gtk.GenericTreeModel.__init__(self)
        self.build_graph(graph, reverse)
        self.calc_depths()
        self.calc_dep_sizes()

    def build_graph(self, graph, reverse):
        self.reverse = reverse
        self.children = {None: []}
        self.node_name = {}
        self.node_available = {}
        for node_id, node in graph.iteritems():
            node_name = node.name
            if not node.compatible:
                node_name = '(%s)' % node_name
            self.add_node(node_id, node_name, node.compatible)
            if node.dist:
                for extra in sorted(node.dist.extras):
                    self.add_node(node_id + '[' + extra +']',
                                  node_name + ' [' + extra + ']',
                                  node.compatible)
        for node_id, node in graph.iteritems():
            for child_id, extras in sorted(node.items()):
                if extras:
                    for extra in sorted(extras):
                        self.add_edge(node_id + '[' + extra + ']', child_id)
                else:
                    self.add_edge(node_id, child_id)
        roots = set(self.children)
        roots.remove(None)
        # XXX: if there are loops, they won't be reachable from roots!
        for children in self.children.values():
            for child_id in children:
                if child_id in roots:
                    roots.remove(child_id)
        self.children[None] = sorted(roots)

    def add_node(self, node_id, node_name, available):
        assert node_id not in self.children
        self.children[node_id] = []
        self.node_name[node_id] = node_name
        self.node_available[node_id] = available

    def add_edge(self, node_id, child_id):
        if child_id not in self.children:
            self.add_node(child_id, '{%s}' % child_id, False)
        if self.reverse:
            self.children[child_id].append(node_id)
        else:
            self.children[node_id].append(child_id)

    def calc_depths(self):
        self.depth = {None: 0}
        queue = [None]
        while queue:
            u = queue.pop(0)
            for v in self.children[u]:
                if v not in self.depth:
                    self.depth[v] = self.depth[u] + 1
                    queue.append(v)

    def calc_dep_sizes(self):
        # Use Brute Force When In Doubt
        self.dep_sizes = {}
        for o in self.children:
            reachable = set()
            stack = [o]
            while stack:
                u = stack.pop()
                for v in self.children[u]:
                    if v not in reachable:
                        reachable.add(v)
                        stack.append(v)
            self.dep_sizes[o] = len(reachable)

    def on_get_flags(self):
        return 0

    _col_types = [str, str, int]

    def on_get_n_columns(self):
        return len(self._col_types)

    def on_get_column_type(self, n):
        return self._col_types[n] 

    def on_get_iter(self, path):
        return path

    def on_get_path(self, rowref):
        return rowref

    def _node_id(self, rowref):
        node_id = None
        for n in rowref:
            node_id = self.children[node_id][n]
        return node_id

    def _node_with_extra_info(self, rowref):
        recursive = False
        seen = set()
        node_id = None
        for n in rowref:
            node_id = self.children[node_id][n]
            if node_id in seen:
                recursive = True
            else:
                seen.add(node_id)
        excessive_depth = len(rowref) > self.depth[node_id]
        return node_id, recursive, excessive_depth

    def on_get_value(self, rowref, column):
        if column == 0:
            return self.node_name[self._node_id(rowref)]
        elif column == 1:
            node_id, recursive, excessive = self._node_with_extra_info(rowref)
            if recursive:
                return 'red'
            elif excessive:
                return 'blue'
            elif not self.node_available[node_id]:
                return 'gray'
        elif column == 2:
            return self.dep_sizes[self._node_id(rowref)]

    def on_iter_next(self, rowref):
        node_id = self._node_id(rowref[:-1])
        idx = rowref[-1] + 1
        if idx >= len(self.children[node_id]):
            return None
        return rowref[:-1] + (idx, )

    def on_iter_children(self, parent):
        if not self.children[self._node_id(parent)]:
            return None # no children
        return parent + (0, )

    def on_iter_has_child(self, rowref):
        node_id, recursive, excessive_depth = self._node_with_extra_info(rowref)
        return bool(self.children[node_id]) and not recursive

    def on_iter_n_children(self, rowref):
        return len(self.children[self._node_id(rowref)])

    def on_iter_nth_child(self, parent, n):
        if not parent:
            parent = ()
        return parent + (n, )

    def on_iter_parent(self, child):
        if not child:
            return None
        return child[:-1]


class MainWindow(object):

    def __init__(self, opts, args):
        w = self.window = gtk.Window()
        self.tree = gtk.TreeView()
        self.tree.set_headers_visible(True)
        self.tree.append_column(gtk.TreeViewColumn("Egg",
                                                   gtk.CellRendererText(),
                                                   text=0, foreground=1))
        if opts.reverse:
            title = "Dependent set size"
        else:
            title = "Dependency set size"
        self.tree.append_column(gtk.TreeViewColumn(title,
                                                   gtk.CellRendererText(),
                                                   text=2, foreground=1))
        self.tree.connect('row-activated', self.row_activated)
        self.tree.connect('test-expand-row', self.test_expand_row)
        s = gtk.ScrolledWindow()
        s.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        s.add(self.tree)
        w.add(s)
        w.set_size_request(600, 400)
        w.show_all()
        w.connect('destroy', gtk.main_quit)
        self.load_tree(opts, args)

    def row_activated(self, tree, path, column):
        if tree.row_expanded(path):
            tree.collapse_row(path)
        else:
            tree.expand_row(path, False)

    def test_expand_row(self, tree, iter, path):
        if tree.get_cursor()[0] == path:
            return False # always allow expansion of the current row
        return self.model._node_with_extra_info(path)[2]

    def load_tree(self, opts, specs):
        def show(name):
            return name not in opts.ignore
        graph = ExtraDiscerningGraph(show=show)
        if specs:
            self.window.set_title("Egg dependencies for %s" % " ".join(specs))
            graph.from_specifications(*specs)
        else:
            self.window.set_title("Egg dependencies of the working set")
            graph.from_working_set()
        self.model = MyTreeModel(graph, opts.reverse)
        self.tree.set_model(self.model)


def main():
    parser = optparse.OptionParser("usage: %prog [options] [specifications]")
    parser.add_option("-i", "--ignore",
                      dest="ignore", action="append",
                      default=['setuptools'],
                      help="project names to ignore")
    parser.add_option("-r", "--reverse",
                      dest="reverse", action="store_true", default=False,
                      help="reverse the dependency graph")
    opts, args = parser.parse_args()
    win = MainWindow(opts, args)
    gtk.main()


if __name__ == '__main__':
    main()
