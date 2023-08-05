"""Useful container classes.

According to Stroustrup:
(http://www.research.att.com/~bs/glossary.html#Gcontainer)

container - (1) object that holds other objects. (2) type of object that
holds other objects. (3) template that generates types of objects that
hold other objects. (4) standard library template such as vector, list,
and map.

Find herein the containers: warehouse and Graph.

This work, including the source code, documentation
and related data, is placed into the public domain.

The orginal author is Robert Brewer, Amor Ministries.

THIS SOFTWARE IS PROVIDED AS-IS, WITHOUT WARRANTY
OF ANY KIND, NOT EVEN THE IMPLIED WARRANTY OF
MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE
ASSUMES _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE
RESULTING FROM THE USE, MODIFICATION, OR
REDISTRIBUTION OF THIS SOFTWARE.

"""

__all__ = ["Graph", "warehouse"]


def warehouse(stock, factory=None):
    """warehouse(stock, factory=None) -> iavailable, iremainder.
    
    Iterate over stock, extending as needed. Once the 'stock' sequence is
    exhausted, the factory function is called to produce a new valid object
    upon each subsequent call to next().
    
    If factory is None, the class of the first item in the sequence is used
    as a constructor. Otherwise, the factory function does not receive any
    arguments, so if your class has mandatory arguments to __init__,
    wrap the class in a function which can supply those.
    
    The most common use for warehouse is to reuse a set of existing
    objects, often because object creation and/or destruction is expensive.
    
    Example:
    
    available, remainder = warehouse(seq)
    for line in order:
        line.use(available.next())
    for item in remainder:
        item.close()
    """
    stock = iter(stock)
    
    def pull():
        for item in stock:
            yield item
        
        if factory is None:
            try:
                local_factory = item.__class__
            except NameError:
                raise ValueError("Empty sequence and no factory supplied.")
        else:
            local_factory = factory
        
        while True:
            yield local_factory()
    
    return pull(), stock


class Graph(dict):
    """An unweighted graph. Can be directed or undirected."""
    
    def __init__(self, data={}, directed=False):
        self.update(data)
        self.directed = directed
        self._cached_paths = {}
        self.declared_paths = {}
    
    def add(self, node):
        if node not in self:
            self[node] = []
            self._cached_paths = self.declared_paths.copy()
    
    def _make_arc(self, node, othernode):
        bucket = self.setdefault(node, [])
        if othernode not in bucket:
            bucket.append(othernode)
    
    def connect(self, node, othernodes):
        """Create an edge between node and each node in othernodes.
        
        Examples:
        Graph().connect('A', ('B', 'C', 'D')) becomes:
              --B
             /
            A---C
             \
              --D
        Graph(directed=True).connect('A', ('B', 'C', 'D')) becomes:
              ->B
             /
            A-->C
             \
              ->D
        """
        try:
            othernodes = iter(othernodes)
        except TypeError:
            othernodes = (othernodes, )
        for othernode in othernodes:
            self._make_arc(node, othernode)
            if not self.directed:
                self._make_arc(othernode, node)
        self._cached_paths = self.declared_paths.copy()
    
    def chain(self, *nodes):
        """Create an edge between each node in sequence.
        
        Examples:
        Graph().chain('A', 'B', 'C', 'D') becomes:
            A--B--C--D
        Graph(directed=True).chain('A', 'B', 'C', 'D') becomes:
            A-->B-->C-->D
        """
        node = nodes[0]
        for nextnode in nodes[1:]:
            self._make_arc(node, nextnode)
            if not self.directed:
                self._make_arc(nextnode, node)
            # Lather, rinse, repeat
            node = nextnode
        self._cached_paths = self.declared_paths.copy()
    
    def shortest_path(self, start, end):
        """A list of nodes, or None if start is valid but no path is found."""
        key = (start, end)
        try:
            return self._cached_paths[key][:]
        except KeyError:
            shortest = self._shortest_path(start, end)
            self._cached_paths[key] = shortest
            if shortest is not None:
                shortest = shortest[:]
            return shortest
    
    def _shortest_path(self, start, end, path=[]):
        """A list of nodes, or None if start is valid but no path is found."""
        if path == []:
            # Test for presence of start in self.
            # Let the KeyError propagate out.
            nodes = self[start]
            path = [start]
        else:
            path = path + [start]
            if start == end:
                return path
            nodes = self[start]
        
        shortest = None
        for node in nodes:
            if node not in path:
                try:
                    newpath = self._shortest_path(node, end, path)
                except KeyError:
                    pass
                else:
                    if newpath:
                        if not shortest or len(newpath) < len(shortest):
                            shortest = newpath
        return shortest
    
    def declare_path(self, path, symmetric=True):
        start, end = path[0], path[-1]
        self.declared_paths[(start, end)] = path[:]
        self._cached_paths[(start, end)] = path[:]
        if symmetric:
            revpath = path[:]
            revpath.reverse()
            self.declared_paths[(end, start)] = revpath
            self._cached_paths[(end, start)] = revpath[:]


