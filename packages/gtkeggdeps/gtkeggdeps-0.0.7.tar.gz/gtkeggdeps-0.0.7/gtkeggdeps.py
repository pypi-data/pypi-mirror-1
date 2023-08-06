#!/usr/bin/env python

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

        graph['B'] == {'X': set(), 'X[extra1]': set(), 'X[extra2]': set()}

    Since the node dict keys are also used for graph traversal, I override
    __getitem__() so that graph['X[extra1'] is the same thing as graph['X'].
    It is perhaps not very nice, but it seems to work.
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


class Node(set):
    """A generic graph node."""

    def __init__(self, name, **kw):
        self.name = name
        self._kwargs = kw
        self.__dict__.update(kw)

    def get_kwargs(self):
        return self._kwargs


class Graph(dict):
    """A generic directed graph.

    Construct the graph by calling ``add_node`` and ``add_edge``.

    Access graph nodes by name via ``graph[node_name]``.  Get an adjacency
    list by ``list(graph[node_name])``.
    """

    def __init__(self): # disallow constructor arguments
        pass

    def add_node(self, node_id, **kw):
        if node_id in self:
            raise ValueError('node already exists: %s' % node_id)
        self[node_id] = Node(node_id, **kw)

    def add_edge(self, node_id, child_id):
        if node_id not in self:
            self.add_node(node_id, False)
        self[node_id].add(child_id)

    def reversed(self):
        clone = self.__class__()
        for node_id, node in self.iteritems():
            clone.add_node(node_id, **node.get_kwargs())
        for node_id, node in self.iteritems():
            for child_id in node:
                clone.add_edge(child_id, node_id)
        return clone


def DependencyGraph(specifications=None, **kw):
    """Construct a package dependency graph.

    The nodes of this graph are packages ("distributions" in
    setuptools-speak) and extras (unlike tl.eggdeps, which uses only
    distributions as nodes).
    """
    # we could use tl.eggdeps.graph.Graph() directly if we can be sure we've
    # got a recent-enough version that supports iter_deps_with_extras, i.e.
    # r1532 or later.
    egggraph = ExtraDiscerningGraph(**kw)
    if specifications is None:
        egggraph.from_working_set()
    else:
        egggraph.from_specifications(*specifications)
    graph = Graph()
    for node_id, node in egggraph.iteritems():
        graph.add_node(node_id, compatible=node.compatible)
        if node.dist:
            # tl.eggdeps did not have the information we need before
            # r1527, so we have to fall back to node.dist.extras.  It's
            # not very accurate -- we should ignore extras that weren't
            # required by any package, since their dependency information is
            # not loaded anyway.
            extras = getattr(node, 'extras_used', node.dist.extras)
            for extra in sorted(extras):
                graph.add_node(node_id + '[' + extra +']',
                              compatible=node.compatible)
    for node_id, node in egggraph.iteritems():
        if hasattr(node, 'iter_deps_with_extras'):
            # available since tl.eggdeps r1532.
            for child_id, dep_extra, extras in sorted(
                                                node.iter_deps_with_extras()):
                if extras:
                    for extra in sorted(extras):
                        graph.add_edge(node_id + '[' + extra + ']', child_id)
                else:
                    graph.add_edge(node_id, child_id)
                if dep_extra:
                    child_id += '[' + dep_extra + ']'
                    if extras:
                        for extra in sorted(extras):
                            graph.add_edge(node_id + '[' + extra + ']', child_id)
                    else:
                        graph.add_edge(node_id, child_id)
        else:
            # the API of tl.eggdeps changed in r1524; before it we used
            # iteritems() to get sets of extras, now we'd be getting dicts
            # of some kind; to get the old data structure we should be
            # using iter_deps().
            iter_deps = getattr(node, 'iter_deps', node.iteritems)
            for child_id, extras in sorted(iter_deps()):
                if extras:
                    for extra in sorted(extras):
                        graph.add_edge(node_id + '[' + extra + ']', child_id)
                else:
                    graph.add_edge(node_id, child_id)
    return graph


class MyTreeModel(gtk.GenericTreeModel):
    """Represent a graph as a tree with duplicated nodes (and subtrees).

    Handles cycles correctly (mostly).
    """

    def __init__(self, graph, reverse=False,
                 show_all_packages_at_top_level=False):
        gtk.GenericTreeModel.__init__(self)
        self.build_graph(graph, reverse, show_all_packages_at_top_level)
        self.calc_depths()
        self.calc_dep_sizes()

    def build_graph(self, graph, reverse, show_all_packages_at_top_level):
        self.reverse = reverse
        self.children = {None: []}
        self.node_name = {}
        self.node_available = {}
        for node_id, node in graph.iteritems():
            node_name = node.name
            if not node.compatible:
                node_name = '(%s)' % node_name
            self.add_node(node_id, node_name, node.compatible)
        for node_id, node in graph.iteritems():
            for child_id in sorted(node):
                self.add_edge(node_id, child_id)
        roots = set(self.children)
        roots.remove(None)
        if not show_all_packages_at_top_level:
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
        if not specs:
            specs = None # convert [] to None
        graph = DependencyGraph(specs, show=show)
        if specs:
            self.window.set_title("Egg dependencies for %s" % " ".join(specs))
            show_all_packages_at_top_level = False
        else:
            self.window.set_title("Egg dependencies of the working set")
            show_all_packages_at_top_level = True
        self.model = MyTreeModel(graph, opts.reverse,
                                 show_all_packages_at_top_level)
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
