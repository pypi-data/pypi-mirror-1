#!/usr/bin/env python

import gtk
import sys
import os
import glob


def debug(fn):
    return fn # XXX 
    def wrapped_fn(*a, **kw):
        print fn.__name__ + '(%s)' % ', '.join(map(repr, a) + ['%s=%r' % (k, v) for k, v in sorted(kw.items())]),
        retval = fn(*a, **kw)
        print '->', retval
        return retval
    return wrapped_fn


class MyTreeModel(gtk.GenericTreeModel):
    """Represent a graph as a tree with duplicated nodes (and subtrees).

    Handles cycles correctly.
    """

    def __init__(self, graph):
        gtk.GenericTreeModel.__init__(self)
        self.graph = graph
        self.children = {None: sorted(graph.roots)}
        for node_id, node in self.graph.iteritems():
            self.children[node_id] = sorted(node)
        self.calc_depths()
        self.calc_dep_sizes()

    def calc_depths(self):
        graph = self.graph
        self.depth = {}
        for root in graph.roots:
            self.depth[root] = 1
        queue = list(graph.roots)
        while queue:
            u = queue.pop(0)
            for v in graph[u]:
                if v not in self.depth:
                    self.depth[v] = self.depth[u] + 1
                    queue.append(v)

    def calc_dep_sizes(self):
        # Use Brute Force When In Doubt
        self.dep_sizes = {}
        for o in self.graph:
            reachable = set()
            stack = [o]
            while stack:
                u = stack.pop()
                for v in self.graph[u]:
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

    def _node(self, rowref):
        node_id = None
        for n in rowref:
            node_id = self.children[node_id][n]
        return self.graph[node_id]

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
        return self.graph[node_id], recursive, excessive_depth

    @debug
    def on_get_value(self, rowref, column):
        if column == 0:
            node = self._node(rowref)
            if node.compatible:
                return node.name
            else:
                return '(%s)' % node.name
        elif column == 1:
            node, recursive, excessive = self._node_with_extra_info(rowref)
            if recursive:
                return 'red'
            elif excessive:
                return 'blue'
            elif not node.compatible:
                return 'gray'
        elif column == 2:
            return self.dep_sizes[self._node_id(rowref)]

    @debug
    def on_iter_next(self, rowref):
        node_id = self._node_id(rowref[:-1])
        idx = rowref[-1] + 1
        if idx >= len(self.children[node_id]):
            return None
        return rowref[:-1] + (idx, )

    @debug
    def on_iter_children(self, parent):
        if not self._node(parent):
            return None # no children
        return parent + (0, )

    @debug
    def on_iter_has_child(self, rowref):
        node, recursive, excessive_depth = self._node_with_extra_info(rowref)
        return bool(node) and not recursive

    @debug
    def on_iter_n_children(self, rowref):
        return len(self.children[self._node_id(rowref)])

    @debug
    def on_iter_nth_child(self, parent, n):
        if not parent:
            parent = ()
        return parent + (n, )

    @debug
    def on_iter_parent(self, child):
        if not child:
            return None
        return child[:-1]


class MainWindow(object):

    def __init__(self):
        w = self.window = gtk.Window()
        self.tree = gtk.TreeView()
        self.tree.set_headers_visible(True)
        self.tree.append_column(gtk.TreeViewColumn("Egg",
                                                   gtk.CellRendererText(),
                                                   text=0, foreground=1))
        self.tree.append_column(gtk.TreeViewColumn("Dependency set size",
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

    def row_activated(self, tree, path, column):
        if tree.row_expanded(path):
            tree.collapse_row(path)
        else:
            tree.expand_row(path, False)

    def test_expand_row(self, tree, iter, path):
        if tree.get_cursor()[0] == path:
            return False # always allow expansion of the current row
        return self.model._node_with_extra_info(path)[2]

    def load_tree(self, specs=()):
        import tl.eggdeps.graph
        graph = tl.eggdeps.graph.Graph(show=lambda name: name != 'setuptools')
        if specs:
            self.window.set_title("Egg dependencies for %s" % " ".join(specs))
            graph.from_specifications(*specs)
        else:
            self.window.set_title("Egg dependencies of the working set")
            graph.from_working_set()
        self.model = MyTreeModel(graph)
        self.tree.set_model(self.model)


def main():
    # XXX
    here = os.path.basename(__file__)
    sys.path.append(os.path.join(here, 'tl.eggdeps-0.2.1-py2.5.egg')) # HACK
    sys.path.append('../z3c.formdemo/src') # HAAAAAAAAAAAAACK
    for name in glob.glob('../z3c.formdemo/eggs/*.egg'): # HAAAAAAAAAAAAACK!
        sys.path.append(name)
    # end XXX
    win = MainWindow()
    win.load_tree(sys.argv[1:])
    gtk.main()


if __name__ == '__main__':
    main()
