zgeo.spatialindex Package Readme
================================

Overview
--------

How to spatially index objects.


Usage
-----

To be indexable, objects must provide IGeoreferenced.
    
    >>> from zgeo.geographer.interfaces import IGeoreferenced
    
Let's create a simple class that implements that interface:
    
    >>> from zope.interface import implements
    >>> class Placemark(object):
    ...     implements(IGeoreferenced)
    ...     def __init__(self, long, lat):
    ...         self.type = 'Point'
    ...         self.coordinates = (long, lat)

Create an instance

    >>> placemark = Placemark(-105.08, 40.59)

Since it directly provides IGeoreferenced, we should get it back when we look
up the adapter

    >>> IGeoreferenced(placemark) == placemark
    True

Next, create a container for it to be indexed in

    >>> from zope.app.container.sample import SampleContainer
    >>> container = SampleContainer()

Any container that is to serve as a spatial index must provide both
IAttributeAnnotatable and ISpatiallyIndexable

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zgeo.spatialindex.interfaces import ISpatiallyIndexable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(container, IAttributeAnnotatable, ISpatiallyIndexable)
    >>> #alsoProvides(container, ISpatiallyIndexable)

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
    >>> index.add('a', IGeoreferenced(placemark))
    >>> len(index)
    1
    >>> [r for r in index]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((-106, 39, -104, 41))]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    []

We can also add tuple records to the index

    >>> index.add('b', (0.5, 39.5, 1.5, 40.5))
    >>> len(index)
    2
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    [('b', (0.5, 39.5, 1.5, 40.5))]

Delete

    >>> del index
    >>> index = ISpatialIndex(container)
    >>> index.remove('a')
    >>> len(index)
    1

    >>> del index
    >>> index = ISpatialIndex(container)
    >>> [r for r in index.intersects((-106, 39, -104, 41))]
    []

Views
-----

Test the query view

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> from zgeo.spatialindex.browser.index import IndexQuery
    >>> query = IndexQuery(container, request)
    >>> query.num_items()
    1
    >>> query.list_query()
    [('b', (0.5, 39.5, 1.5, 40.5))]

Management view

    >>> from zgeo.spatialindex.browser.manage import IndexManage
    >>> mgmt = IndexManage(container, request)
    >>> mgmt.rebuild()
    >>> query.num_items()
    0

Add the placemark to the container and rebuild. We'll have one item.

    >>> container['a'] = placemark
    >>> mgmt.rebuild()
    >>> query.num_items()
    1


Tear down

    >>> index.destroy()



