
import random
import timeit

try:
    import pkg_resources
    pkg_resources.require('Quadtree')
except:
    pass

from quadtree import Quadtree

# a very basic Geometry
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Scatter points randomly in a 1x1 box
count = 1000
index_extent = [-180, -90, 180, 90]
points = []
index = Quadtree(index_extent)
for i in xrange(count):
    x = random.random()
    y = random.random()
    points.append(Point(x, y))
    index.add(i, [x, y, x, y])

bbox = [0.2, 0.3, 0.3, 0.4]

print count, "points"
print "Index extent: ", index_extent
print "Query box: ", bbox
print ""

# Brute force all points within a 0.1x0.1 box
s = """
hits = [p for p in points if p.x >= bbox[0] and p.x <= bbox[2] and p.y >= bbox[1] and p.y <= bbox[3]]
"""
t = timeit.Timer(stmt=s, setup='from __main__ import points, bbox')
print "\nBrute Force:"
print len([p for p in points if p.x >= bbox[0] and p.x <= bbox[2] and p.y >= bbox[1] and p.y <= bbox[3]]), "hits"
print "%.2f usec/pass" % (1000000 * t.timeit(number=100)/100)

# 0.1x0.1 box using likely_intersection

s = """
hits = [points[id] for id in index.likely_intersection(bbox)]
"""
t = timeit.Timer(stmt=s, setup='from __main__ import points, index, bbox')
print "\nLikely Intersection:"
print len([points[id] for id in index.likely_intersection(bbox)]), "hits"
print "%.2f usec/pass" % (1000000 * t.timeit(number=100)/100)

# 0.1x0.1 box using likely_intersection, and a final brute force pass
# over hits to eliminate false positives.

s = """
likelies = [points[id] for id in index.likely_intersection(bbox)]
hits = [p for p in likelies if p.x >= bbox[0] and p.x <= bbox[2] and p.y >= bbox[1] and p.y <= bbox[3]]
"""
t = timeit.Timer(stmt=s, setup='from __main__ import points, index, bbox')
print "\nLikely Intersection with false positive mop-up:"
likelies = [points[id] for id in index.likely_intersection(bbox)]
print len([p for p in likelies if p.x >= bbox[0] and p.x <= bbox[2] and p.y >= bbox[1] and p.y <= bbox[3]]), "hits"
print "%.2f usec/pass" % (1000000 * t.timeit(number=100)/100)


