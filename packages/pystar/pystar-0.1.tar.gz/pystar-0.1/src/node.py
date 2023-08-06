"""
Implementation of A* for abstract nodes.  To apply the algorithm you must
subclass L{Node} and override the methods listed there.
"""

from heapq import heappush, heappop, heapify

def abstract(func):
    """Decorator for abstract functions."""
    def must_implement(self, *args, **kw):
        raise NotImplementedError(func.__name__ +
                                  ' must be implemented in subclass')
    return must_implement

class Node(object):
    """
    Base class for A* nodes.

    When subclassing, the methods L{adjacent}, L{distance},
    L{estimated_distance} and L{__eq__} must be overridden.

    @ivar gfunc: G function score (cost to get here from start).
    @ivar hfunc: H function score (estimated cost to get to goal).
    @ivar ffunc: Sum of G and H score.
    """

    def find_path(self, goal):
        """
        Find a path from this node to a goal node.  This is the
        actual implementation of A*.

        @param goal: The goal node.
        @type goal: A L{Node} instance.
        @return: List of L{Node} instances, or C{None} if there is no path.
        """

        openlist = []           # Nodes to be considered.
        closedlist = {}         # Nodes already visited.
        came_from = {}          # Pointers to previous nodes.

        # Initialize open list with current node.
        heappush(openlist, self)
        self.ffunc = self.gfunc = self.hfunc = 0

        while openlist:
            # Get the node with smallest cost, and mark it as visited.
            x = heappop(openlist)
            closedlist[x] = True

            # If it's the goal, we've finished.  Woo hoo!
            if x == goal:
                path = [goal]

                # Build and return the path from the node history.
                while came_from.has_key(x):
                    x = came_from[x]
                    path.insert(0, x)

                return path

            # Otherwise, consider all adjacent nodes.
            for y in x.adjacent():
                # If it's been visited, ignore it.
                if y in closedlist:
                    continue

                # Get the distance to it.
                d = x.distance(y)

                # If blocked, ignore it.
                if d is None:
                    continue

                # Get G score.
                latest_g_score = x.gfunc + d

                # Has it been seen before?
                node_not_seen = y not in openlist

                # Score is better if node not seen, or G score is lower.
                score_is_better = node_not_seen or latest_g_score <= y.gfunc

                # If not seen, estimate distance to goal (H score).
                if node_not_seen:
                    y.hfunc = y.estimated_distance(goal)

                # If G score is better, update where we came from and
                # recalculate total F score.
                if score_is_better:
                    came_from[y] = x
                    y.gfunc = latest_g_score
                    y.ffunc = y.gfunc + y.hfunc

                if node_not_seen:
                    # Add node to list.  Must be done after setting F
                    # score, or it won't be sorted into correct place.
                    heappush(openlist, y)
                elif score_is_better:
                    # Already in list, but its score changed.  Need to
                    # re-heapify.
                    heapify(openlist)

        # No path found.
        return None

    @abstract
    def adjacent(self):
        """
        Return list of adjacent nodes to this one.  Must be overridden.

        @return: List of L{Node} instances.
        """

    @abstract
    def distance(self, other):
        """
        Return the distance from this node to an adjacent one.  Must be
        overridden.

        @return: Distance, or C{None} if other node is not adjacent, or
        blocked.
        """

    @abstract
    def estimated_distance(self, other):
        """
        Return the estimated distance from this node to another.  Must be
        overridden.

        @note: In order to properly implement the A* algorithm, this
        function must never overestimate the distance.

        @return: Estimated distance.
        """

    @abstract
    def __eq__(self, other):
        """
        Return whether two nodes are the same.  Must be overridden.
        """

    def __cmp__(self, other):
        val = cmp(self.ffunc, other.ffunc)
        if not val: val = cmp(id(self), id(other))
        return val

class AstarError(Exception):
    """An A* exception."""

if __name__ == "__main__":
    n1 = Node()
    n2 = Node()
    print n1.find_path(n2)
