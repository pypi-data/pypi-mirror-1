Treemap: A treemap viewer for python.

Requires matplotlib (I didn't put this in the automated requirements as setuptools 
doesn't seem to find if if installed on your system).

Usage:

Using this requires that you pass in the root node of the tree, along with methods
to return the children, size, color of a node.

Optionally, a method for the how to get the name of a node (default str) and
the margin around nodes can be provided.  Note a non-zero margin probably damages

Sample code:

import operator
import random
import pylab

size_cache = {}

# the tree is nested tuples
tree= ((5,(3,5,2,(0.1,0.1,0.6),1)), 4, (5,2,(2,3,(3,2, (2,5,2),2)),(3,3)), (3,2,(0.2,0.2,0.2)) )

# the size of a node is the sum of the sizes of its leaf nodes
def size(thing):
    if isinstance(thing, int) or isinstance(thing, float):
        return thing
    if thing in size_cache:
        return size_cache[thing]
    else:
        size_cache[thing] = reduce(operator.add, [size(x) for x in thing])
        return size_cache[thing]

# random color (note r,g,b triples could be specified here)
def random_color(thing):
    return random.random()  #colorsys.hsv_to_rgb(0.5, random.random(), 1)

# build the treemap object
Treemap(tree, iter, size, random_color, margin=0.01)    

# show it!
pylab.show()
