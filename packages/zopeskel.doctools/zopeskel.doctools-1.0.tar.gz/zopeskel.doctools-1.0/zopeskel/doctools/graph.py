"""
Visualize a directed graph of paster entry point dependencies.

Constructs a GraphViz dot file directly without the use of silly GraphViz
bindings. Just throw the output into one of many freely available web
services like http://ashitani.jp/gv/
"""

class Graph(object):
    """
    Methods to visualize paster entry point dependencies.
    """

    def __init__(self,
                 template_bundle=None,
                 entry_point_group_name=None,
                 detail=False,
                 default_bundle='zopeskel'):
        super(Graph,self).__init__()
        self.template_bundle = template_bundle
        self.entry_point_group_name = entry_point_group_name
        self.detail = detail
        self.default_bundle = default_bundle
        self.nodes = {}

    def create(self):
        """
        Create the dot language commands for GraphViz.

        If no entry group specified, walk each entry group in the entry map.
        Walk each entry point in the entry group.
        Add nodes for entry point to graph.
        Create an edge for each base/class pair.
        Format a diagraph of edges.
        """

        import pkg_resources

        if self.template_bundle:
            # filter to entry points in template bundle only
            if self.entry_point_group_name:
                # single entry point group
                entry_map = pkg_resources.get_entry_map(self.template_bundle)
                entry_point_group = \
                    entry_map[self.entry_point_group_name].values()
                self.parse(self.entry_point_group_name,entry_point_group)
            else:
                # all entry point groups
                entry_map = pkg_resources.get_entry_map(self.template_bundle)
                for entry_point_group_name in entry_map:
                    entry_point_group = \
                        entry_map[entry_point_group_name].values()
                    self.parse(entry_point_group_name,entry_point_group)
        else:
            # all entries points
            if self.entry_point_group_name:
                # single entry point group
                entry_point_group = [entry_point for entry_point
                in pkg_resources.iter_entry_points(self.entry_point_group_name)]
                self.parse(self.entry_point_group_name,entry_point_group)
            else:
                # all entry points in all entry point groups in default bundle
                entry_map = pkg_resources.get_entry_map(self.default_bundle)
                for entry_point_group_name in entry_map:
                    entry_point_group = [entry_point for entry_point
                    in pkg_resources.iter_entry_points(entry_point_group_name)]
                    self.parse(entry_point_group_name,entry_point_group)

        if self.entry_point_group_name:
            title = self.entry_point_group_name
        elif self.template_bundle:
            title = self.template_bundle
        else:
            title = self.default_bundle
        graph = ['digraph %s {' % title]
        for class_name,node in self.nodes.items():
            for base_name in node['base_names']:
                node['base_name'] = base_name
                graph.append('%(base_name)s -> %(class_name)s' % node)
            if node['module']:
                if self.detail:
                    graph.append(('%(class_name)s [label=\"' +
                                  'entry %(entry_point_name)s\\n' +
                                  'group %(entry_point_group_name)s\\n' +
                                  'class %(class_name)s\\n' +
                                  'module %(module_name)s'
                                  '\",fillcolor=palegoldenrod]')
                                 % node)
                else:
                    graph.append(('%(class_name)s [label=\"' +
                                  '%(entry_point_name)s' +
                                  '\",fillcolor=palegoldenrod]')
                                 % node)
            else:
                if self.detail:
                    graph.append(('%(class_name)s [label=\"type %(class_name)s\",' +
                                                  'fillcolor=lightsalmon]')
                                 % node)
                else:
                    graph.append(('%(class_name)s [label=\"%(class_name)s\",' +
                                                  'fillcolor=lightsalmon]')
                                 % node)

        if self.detail:
            graph.append('object [label=\"type object\",fillcolor=lightsalmon]')
        else:
            graph.append('object [label=\"object\",fillcolor=lightsalmon]')
        graph.append('}')
        graph = '\n'.join(graph)
        return graph

    def parse(self,entry_point_group_name,entry_point_group):
        """
        Add the nodes for an entry point to graph.

        Add a node for the entry point's class.
        Recursively walk the base classes for each entry point.
        """
        for entry_point in entry_point_group:
            entry_point_name = entry_point.name
            module_name = entry_point.module_name
            module = __import__(module_name, globals(),locals(),(module_name,))
            class_names = entry_point.attrs
            for class_name in class_names:
                cls = getattr(module,class_name)
                if isinstance(cls,type):
                    bases = cls.__bases__
                    base_names = [base.__name__ for base in bases]
                    self.add_node(cls,class_name,
                                  bases,base_names,
                                  module,module_name,
                                  entry_point,entry_point_name,
                                  entry_point_group,entry_point_group_name)
                    # recurse through the superclasses
                    # for each entry point
                    # adding a node for each
                    while bases != (object,):
                        bases_bases = []
                        for base in bases:
                            base_name = base.__name__
                            base_bases = base.__bases__
                            for base_base in base_bases:
                                if base_base not in bases_bases:
                                    bases_bases.append(base_base)
                            base_base_names = [base_base.__name__
                                               for base_base in base_bases]
                            self.add_node(base,base_name,
                                          base_bases,base_base_names)
                        bases = tuple(bases_bases)
        return self.nodes

    def add_node(self,cls,class_name,
                      bases,base_names,
                      module=None,module_name=None,
                      entry_point=None,entry_point_name=None,
                      entry_point_group=None,entry_point_group_name=None):
        """
        Add a node to the directed graph.

        If the node has already been added to the graph, check if it needs
            entry point data.
        If the node has not already been added to the graph, then do so.
        """

        if module:
            node = self.nodes.get(class_name)
            if node:
                if not node['module']:
                    node['module'] = module
                    node['module_name'] = module_name
                    node['entry_point'] = entry_point
                    node['entry_point_name'] = entry_point_name
                    node['entry_point_group'] = entry_point_group
                    node['entry_point_group_name'] = entry_point_group_name
        return self.nodes.setdefault(class_name,{'class':cls,
                                                 'class_name': class_name,
                                                 'bases':bases,
                                                 'base_names':base_names,
                                                 'module':module,
                                                 'module_name':module_name,
                                                 'entry_point':entry_point,
                                                 'entry_point_name':
                                                     entry_point_name,
                                                 'entry_point_group':
                                                     entry_point_group,
                                                 'entry_point_group_name'
                                                     :entry_point_group_name,
                                                })

def _main(template_bundle=None,entry_point_group_name=None,detail=False):
    """
    Visualize a directed graph of paster template dependencies.
    """
    return Graph(template_bundle,
                 entry_point_group_name,
                 detail).create()

def graph():
    print _main('zopeskel','paste.paster_create_template')

if __name__ == '__main__':
    graph()
