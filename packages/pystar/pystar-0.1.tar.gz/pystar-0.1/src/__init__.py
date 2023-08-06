'''
This package implements the A* graph search algorithm.  The following
description (and the algorithm implementation) is taken from
U{Wikipedia<http://en.wikipedia.org/wiki/A%2A>}; see that article for more
information.

A* (pronounced "A star") is a best-first graph search algorithm that finds
the least-cost path from a given initial node to one goal node (out of one
or more possible goals).  It uses a distance-plus-cost heuristic function
(usually denoted M{f(x)} to determine the order in which the search visits
the nodes in the tree.  The distance-plus-cost heuristic is a sum of two
functions: the path-cost function (usually denoted M{g(x)}, which may or
may not be a heuristic) and an admissible "heuristic estimate" of the
distance to the goal (usually denoted M{h(x)}).  The path-cost function
M{g(x)} is the cost from the starting node to the current node.

Since the M{h(x)} part of the M{f(x)} function must be an admissible
heuristic, it must not overestimate the distance to the goal.  Thus for an
application like routing, M{h(x)} might represent the straight-line
distance to the goal, since that is physically the smallest possible
distance between any two points (or nodes for that matter).

A* incrementally searches all routes leading from the starting point until
it finds the shortest path to a goal.  Like all informed search algorithms,
it searches first the routes that appear to be most likely to lead towards
the goal.  What sets A* apart from a greedy best-first search is that it
also takes the distance already traveled into account (the M{g(x)} part of
the heuristic is the cost from the start, and not simply the local cost
from the previously expanded node).

The algorithm traverses various paths from start to goal.  For each node
traversed, it computes 3 values:

  - G score -- the actual shortest distance traveled from source to current node
  - H score -- estimated (or "heuristic") distance from current node to goal
  - F score -- sum of G score and H score

Starting with a given node, the algorithm expands the node with the lowest
M{f(x)} score -- the node that has the lowest cost-per-benefit.  A*
maintains a set of partial solutions -- unexpanded leaf nodes of expanded
nodes -- stored in a priority queue.  The priority assigned to a path M{x}
is determined by the function M{f(x) = g(x) + h(x)}.  The function
continues until a goal has a lower M{f(x)} score than any node in the queue
(or until the tree is fully traversed).  Multiple goals may be passed over
if there is a path that may lead to a lower-cost goal.
'''

from node import Node, AstarError
from grid import Grid

__author__  = 'Glenn Hutchings'
__contact__ = 'zondo42@googlemail.com'
__version__ = '0.1'
__license__ = 'GNU General Public License, version 2'
