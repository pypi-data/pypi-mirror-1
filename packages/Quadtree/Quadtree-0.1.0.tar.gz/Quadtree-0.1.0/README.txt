
Quadtree: spatial index for Python GIS
======================================

Whether for Python in-memory feature stores, Plone content, or whatever -- we
need a simple spatial index to speed up the search for objects that intersect
with a given spatial bounding box.

The simplest, most tried-and-true, open source spatial index is shapelib's
(http://shapelib.maptools.org) quadtree. It's been improving the performance of
MapServer applications for years. The quadtree itself is completely separable
from any shapefile. We can use it with arbitrary Python object collections.


Quadtree Protocol
-----------------

In a nutshell:

  >>> index.add(id=id, bounds=(left, bottom, right, top))
  >>> [n for n in index.likely_intersection((left, bottom, right, top))]
  [id]

This resembles a subset of the set protocol, and is all we need to begin.
*add* indexes a new object by id, *likely_intersection* returns an iterator
over ids where the node containing the id intersects with the specified
bounding box. This method can produce false positives. It is up to the
application to handle such false positive index hits and to map ids to objects.


Installation
------------

$ python setup.py install


Usage
-----

See tests/QuadTree.txt.


Performance
-----------

Even with the false positives, Quadtree wins over brute force intersection
evaluations implemented in Python once you have more than ~20 points. See the
tests/benchmarks.py file for a comparison.


Support
-------

For current information about this project, see

http://icon.stoa.org/trac/pleiades/wiki/QuadTree

If you have questions, please consider joining our software support list:

http://icon.stoa.org/trac/pleiades/wiki/PleiadesSoftwareList


About Pleiades
--------------

Pleiades is an international research network and associated web portal and
content management system devoted to the study of ancient geography. 

See http://icon.stoa.org/trac/pleiades/wiki.

Funding for the creation of this software was provided by a grant from the 
U.S. National Endowment for the Humanities (http://www.neh.gov).

