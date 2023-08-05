Spatial Indexes
===============

zgeo.spatialindex provides a spatial bounding box index that plugs into the
Zope Catalog.

ISpatiallyBounded is an interface essential to the bounding box index

    >>> from zope.interface import implements
    >>> from zope.location.interfaces import ILocation
    >>> import zgeo.geographer.example
    >>> class Placemark(zgeo.geographer.example.Placemark):
    ...     implements(ILocation)

    >>> placemark1 = Placemark()
    >>> from zgeo.geographer.interfaces import IGeoreferenced
    >>> geo = IGeoreferenced(placemark1)
    >>> geo.setGeoInterface('Point', (-105.08, 40.59))
    >>> from zgeo.spatialindex.interfaces import IBounded
    >>> bounded = IBounded(placemark1)
    >>> bounded.bounds
    (-105.08, 40.590000000000003, -105.08, 40.590000000000003)

Next, create a catalog:

    >>> from zgeo.spatialindex.catalog import Catalog
    >>> cat = Catalog()

and add a bounding box index:

    >>> from zgeo.spatialindex.index import BoundsIndex
    >>> cat['bounds'] = BoundsIndex('bounds', IBounded)

Index 2 placemark objects

    >>> placemark2 = Placemark()
    >>> geo = IGeoreferenced(placemark2)
    >>> geo.setGeoInterface('Point', (0.0, 0.0))

    >>> cat.index_doc(1, placemark1)
    >>> cat.index_doc(2, placemark2)

Query using bounds that encompass neither

    >>> list(cat.apply({'bounds': (-110, 30, -105, 35)}))
    []

Using bounds that encompass only the first

    >>> list(cat.apply({'bounds': (-110, 40, -105, 45)}))
    [1L]

And with bounds that encompass both

    >>> list(cat.apply({'bounds': (-180, -90, 180, 90)}))
    [1L, 2L]

We can unindex objects:

    >>> cat.unindex_doc(1)
    >>> list(cat.apply({'bounds': (-180, -90, 180, 90)}))
    [2L]

and reindex objects:

    >>> geo = IGeoreferenced(placemark2)
    >>> geo.setGeoInterface('Point', (-105.0, 40.0))
    >>> cat.index_doc(2, placemark2)
    >>> list(cat.apply({'bounds': (-110, 40, -105, 45)}))
    [2L]

Clear

    >>> cat.clear()
    >>> len(cat['bounds'].backward)
    0
    >>> list(cat.apply({'bounds': (-180, -90, 180, 90)}))
    []

Finally, let's test our spatial catalog factory:

    >>> from zope.app.folder import Folder
    >>> places = Folder()
    >>> from zgeo.spatialindex.site import createLocalSpatialCatalog
    >>> createLocalSpatialCatalog(places)
    >>> sm = places.getSiteManager()

Can has an IIntIds utility?

    >>> from zope.app.intid.interfaces import IIntIds
    >>> intids = sm.getUtility(IIntIds)
    >>> intids
    <zope.app.intid.IntIds object at ...>

Can has a catalog?

    >>> from zope.app.catalog.interfaces import ICatalog
    >>> cat = sm.getUtility(ICatalog)
    >>> cat
    <zgeo.spatialindex.catalog.Catalog object at ...>
    >>> cat['bounds']
    <zgeo.spatialindex.index.BoundsIndex object at ...>

Adding a placemark to the folder should result in new intid items, but no
catalog entry because the placemark isn't georeferenced. First, however, we need to provide subscribers to IObjectAddedEvent:

    >>> from zope.component import provideHandler
    >>> from zope.app.intid import addIntIdSubscriber, removeIntIdSubscriber
    >>> provideHandler(addIntIdSubscriber)
    >>> provideHandler(removeIntIdSubscriber)

    >>> placemark3 = Placemark()
    >>> placemark3.__name__ = '3'
    >>> placemark3.__parent__ = places
    >>> places['3'] = placemark3

    >>> list(intids.refs)
    []

