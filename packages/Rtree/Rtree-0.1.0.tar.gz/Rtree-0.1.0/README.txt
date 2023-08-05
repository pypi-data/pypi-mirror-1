
Rtree: spatial index for Python GIS
===================================

Whether for Python in-memory feature stores, Plone content, or whatever -- we
need a simple spatial index to speed up the search for objects that intersect
with a given spatial bounding box.


Index Protocol
--------------

In a nutshell:

  >>> index.add(id=id, bounds=(left, bottom, right, top))
  >>> [n for n in index.intersection((left, bottom, right, top))]
  [id]

This resembles a subset of the set protocol, and is all we need to begin.
*add* indexes a new object by id, *intersection* returns an iterator over ids
where the node containing the id intersects with the specified bounding box.
The *intersection* method is exact, with no false positives and no missed data.


Installation
------------

$ python setup.py install

This installs an egg. If you'd rather stick with the old-school distributions,
use

$ python setup.py install --root / --single-version-externally-managed


Usage
-----

See tests/R-Tree.txt.


Performance
-----------


See the tests/benchmarks.py file for a comparison.


Support
-------

For current information about this project, see

http://trac.gispython.org/projects/PCL/wiki/ArrTree

If you have questions, please consider joining our community list:

http://trac.gispython.org/projects/PCL/wiki/CommunityList

