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
   
    >>> from persistent import Persistent
    >>> from zope.interface import implements
    >>> class Placemark(Persistent):
    ...     implements(IGeoreferenced)
    ...     __name__ = __parent__ = None
    ...     type = 'Point'
    ...     coordinates = []
    ...     def __init__(self, name, long, lat):
    ...         self.type = 'Point'
    ...         self.coordinates = [long, lat]

Create an instance

    >>> placemark = Placemark('a', -105.08, 40.59)

Since it directly provides IGeoreferenced, we should get it back when we look
up the adapter

    >>> IGeoreferenced(placemark) == placemark
    True

    >>> from zope.app.container.sample import SampleContainer
    >>> container = SampleContainer()

Any container that is to serve as a spatial index must provide both
IAttributeAnnotatable and ISpatiallyIndexable

Make the container indexable

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zgeo.spatialindex.interfaces import ISpatiallyIndexable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(container, IAttributeAnnotatable, ISpatiallyIndexable)
    >>> from zope.app.keyreference.persistent import KeyReferenceToPersistent
    >>> from persistent.interfaces import IPersistent
    >>> from zope.component import provideAdapter
    >>> provideAdapter(KeyReferenceToPersistent, adapts=[IPersistent])
    >>> from zope.app.intid import IntIds
    >>> from zope.app.intid.interfaces import IIntIds
    >>> intids = IntIds()
    >>> from zope.component import provideUtility
    >>> provideUtility(intids, IIntIds)

Register the annotation and index adapters

    >>> from zgeo.spatialindex.index import SpatialIndex
    >>> provideAdapter(SpatialIndex)
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> from zope.annotation.interfaces import IAnnotations
    >>> provideAdapter(AttributeAnnotations, [IAttributeAnnotatable], IAnnotations)

Put the container and placemark in a dummy database

    >>> from ZODB.DemoStorage import DemoStorage
    >>> from ZODB import DB
    >>> db = DB(DemoStorage())
    >>> conn = db.open()
    >>> root = conn.root()

Now we can adapt the container to ISpatialIndex and add the placemark to the
index

    >>> root['container'] = container
    >>> container['a'] = placemark
    >>> placemark.__name__ = 'a'
    >>> import transaction
    >>> transaction.commit() # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    PicklingError: ...
    >>> from zgeo.spatialindex.interfaces import ISpatialIndex
    >>> index = ISpatialIndex(container)
    >>> index.add(placemark) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    KeyError: <Placemark object at ...>

Placemark needs to be registered with the integer utility

    >>> from zope.component import getUtility
    >>> intids = getUtility(IIntIds)
    >>> intids.register(placemark) > 0
    True

    >>> index.add(placemark)
    >>> len(index)
    1
    >>> [r for r in index]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((-106, 39, -104, 41))]
    [('a', (-105.08, 40.590000000000003, -105.08, 40.590000000000003))]
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    []

Deletion

    >>> index = ISpatialIndex(container)
    >>> index.remove(placemark)
    >>> len(index)
    0

We can also add tuple records to the index

    >>> index.add(placemark, (0.5, 39.5, 1.5, 40.5))
    >>> len(index)
    1
    >>> [r for r in index.intersects((0.0, 39, 2.0, 41))]
    [('a', (0.5, 39.5, 1.5, 40.5))]

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
    [('a', (0.5, 39.5, 1.5, 40.5))]

Management view

    >>> from zgeo.spatialindex.browser.manage import IndexManage
    >>> mgmt = IndexManage(container, request)
    >>> mgmt.rebuild()
    >>> query.num_items()
    1

Tear down

    >>> index.destroy()



