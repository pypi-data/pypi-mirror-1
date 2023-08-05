zgeo.spatialindex Package Readme
================================

Overview
--------

    How to index content.

Usage
-----

To be indexable, objects must provide zgeo.geographer.interfaces.IGeoItem.
    
    >>> from zgeo.geographer.interfaces import IGeoItem
    
Let's create 2 example classes to implement that interface:
    
    >>> from zope.interface import implements
    >>> from zgeo.geographer.interfaces import IGeometry

    >>> class Point(object):
    ...     implements(IGeometry)
    ...     def __init__(self, long, lat):
    ...         self.type = 'Point'
    ...         self.long = long
    ...         self.lat = lat
    ...     @property
    ...     def coordinates(self):
    ...         return (self.long, self.lat)
    ...     @property
    ...     def __geo_interface__(self):
    ...         return {'type': self.type, 'coordinates': self.coordinates}

    >>> class Placemark(object):
    ...     implements(IGeoItem)
    ...     def __init__(self, id, summary, long, lat):
    ...         self.id = id
    ...         self.properties = {'summary': summary}
    ...         self.geometry = Point(long, lat)
    ...     @property
    ...     def __geo_interface__(self):
    ...         return {
    ...             'type': 'Feature',
    ...             'id': self.id,
    ...             'properties': self.properties,
    ...             'geometry': self.geometry.__geo_interface__
    ...             }

Now, create a placemark instance

    >>> placemark = Placemark('a', "Place marked 'A'", -105.08, 40.59)

Since it directly provides IGeoItem, we should get it back when we look up the
adapter

    >>> IGeoItem(placemark) == placemark
    True

Next, create a container for it to be indexed in

    >>> from zope.app.container.sample import SampleContainer
    >>> container = SampleContainer()

Any container that is to serve as a spatial index must provide both
IAttributeAnnotatable and ISpatiallyIndexable

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zgeo.spatialindex.interfaces import ISpatiallyIndexable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(container, IAttributeAnnotatable)
    >>> alsoProvides(container, ISpatiallyIndexable)

Register the annotation and index adapters

    >>> from zope.component import provideAdapter
    >>> from zgeo.spatialindex.index import SpatialIndex
    >>> provideAdapter(SpatialIndex)
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> from zope.annotation.interfaces import IAnnotations
    >>> provideAdapter(AttributeAnnotations, [IAttributeAnnotatable], IAnnotations)

Now we can adapt the container to ISpatialIndex and add the placemark to the
index

    >>> from zgeo.spatialindex.interfaces import ISpatialIndex
    >>> index = ISpatialIndex(container)
    >>> index.add(IGeoItem(placemark))
    >>> len(index)
    1
    >>> [r for r in index]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((-106, 39, -104, 41))]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    []

We can also add tuple records to the index

    >>> index.add(('b', (0.5, 39.5, 1.5, 40.5)))
    >>> len(index)
    2
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    [('b', (0.5, 39.5, 1.5, 40.5))]

Delete

    >>> del index
    >>> index = ISpatialIndex(container)
    >>> index.remove(IGeoItem(placemark))
    >>> len(index)
    1

    >>> del index
    >>> index = ISpatialIndex(container)
    >>> [r for r in index.intersects((-106, 39, -104, 41))]
    []

Tear down

    >>> index.destroy()

