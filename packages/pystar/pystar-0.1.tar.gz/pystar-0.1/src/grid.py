"""
Implementation of A* on a regular grid of cells.  Each cell can have a
numeric weight, which is the cost of moving to it, or a weight of C{None},
which means that cell is blocked.
"""

from node import Node, AstarError
from math import hypot

class Grid(object):
    """
    Container for a rectangular grid of L{GridNode}s.

    @ivar cost: Total cost of the last path found by L{find_path}.
    """

    def __init__(self, width, height, diag = False):
        """
        @param width: Width of the grid.
        @param height: Height of the grid.
        @param diag: Whether to allow diagonal moves.
        """

        self.width = width
        self.height = height
        self.nodes = {}
        self.cost = None

        for x in xrange(width):
            for y in xrange(height):
                self.nodes[x, y] = GridNode(self, (x, y))

        offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        if diag:
            offsets.extend(((-1, -1), (-1, 1), (1, -1), (1, 1)))

        for x in xrange(width):
            for y in xrange(height):
                node = self.nodes[x, y]
                for i, j in offsets:
                    other = self.nodes.get((x + i, y + j), None)
                    if other: node.adjlist.append(other)

    def find_path(self, frompos, topos):
        """
        Find a minimum-cost path from one cell to another.
        @param frompos: From this cell.
        @type frompos: 2-tuple
        @param topos: To this cell.
        @type topos: 2-tuple
        @return: List of 2-tuples representing the path, including the
            start and end points.
        @raise AstarError: if either cell not in grid.
        """

        node = self._find_node(frompos)
        other = self._find_node(topos)
        path = node.find_path(other)

        if path:
            self.cost = path[-1].gfunc
            return [(node.x, node.y) for node in path]

        return None

    def set_weight(self, pos, weight):
        """
        Set the weighting of a cell.  If set to C{None}, the cell is blocked.
        @param pos: Cell position.
        @type pos: 2-tuple
        @param weight: Weighting.
        @type weight: Numeric value, or C{None}
        @raise AstarError: if cell not in grid.
        """

        node = self._find_node(pos)
        node.weight = weight

    def get_weight(self, pos):
        """
        Get the weighting of a cell.
        @param pos: Cell position.
        @type pos: 2-tuple
        @return: Weighting.
        @raise AstarError: if cell not in grid.
        """

        node = self._find_node(pos)
        return node.weight

    def diagram(self, path = None, start = 'SS', end = 'EE', onpath = '**',
                background = "..", blocked = 'XX', vsep = ' '):
        """
        Create an ASCII diagram of a grid containing a path.
        @return: Diagram string suitable for printing.
        """

        grid = []

        for y in xrange(self.height):
            grid.append([background] * self.width)

        if path:
            for x, y in path:
                grid[y][x] = onpath

            x, y = path[0]; grid[y][x] = start
            x, y = path[-1]; grid[y][x] = end

        for x in xrange(self.width):
            for y in xrange(self.height):
                node = self.nodes[x, y]
                if node.weight is None:
                    grid[y][x] = blocked

        lines = [vsep.join(grid[y]) for y in xrange(self.height)]
        return "\n".join(lines)

    def _find_node(self, pos):
        try:
            return self.nodes[tuple(pos)]
        except KeyError:
            raise AstarError("%s not in grid" % str(pos))

class GridNode(Node):
    """
    Grid-based A* node.
    """

    def __init__(self, grid, pos):
        self.grid = grid
        self.x = pos[0]
        self.y = pos[1]
        self.weight = 0
        self.adjlist = []

    def adjacent(self):
        """Return list of adjacent grid nodes."""
        return self.adjlist

    def distance(self, other):
        """Return distance to adjacent grid node."""
        if other in self.adjlist and other.weight is not None:
            return hypot(self.x - other.x, self.y - other.y) + other.weight

        return None

    def estimated_distance(self, other):
        """Return estimated distance to another grid node."""
        return hypot(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return id(self) == id(other)

def _test(size = 20):
    g = Grid(size, size, True)

    min = size / 3
    max = 2 * size / 3
    for x in xrange(min, max):
        for y in xrange(min, max):
            g.set_weight((x, y), None)

    path = g.find_path((1, 1), (size - 2, size - 2))
    print g.diagram(path)

if __name__ == "__main__":
    if True:
        import cProfile as profile
        from pstats import Stats
        profile.run("_test()", "grid.dat")
        Stats("grid.dat").sort_stats('time').print_stats()
    else:
        _test()
