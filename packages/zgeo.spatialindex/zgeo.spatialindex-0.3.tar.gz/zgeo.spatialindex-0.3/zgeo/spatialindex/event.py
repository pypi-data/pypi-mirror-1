from zope.component import getUtility
from zope.interface import implements
from zope.app.intid.interfaces import IIntIds
from zope.app.intid.interfaces import IntIdRemovedEvent
from zope.app.intid.interfaces import IntIdAddedEvent
from zope.location.interfaces import ILocation
from zope.component import adapter, getAllUtilitiesRegisteredFor
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.event import notify
from zgeo.spatialindex.site import get_catalog, createLocalSpatialCatalog
from zgeo.spatialindex.interfaces import IAddSpatialContainerEvent
from zope.security.proxy import removeSecurityProxy
from zgeo.geographer.interfaces import IGeoreferenceable
from zope.app.generations.utility import findObjectsProviding


class AddSpatialContainerEvent(object):
    implements(IAddSpatialContainerEvent)
    def __init__(self, container):
        self.object = container


@adapter(IAddSpatialContainerEvent)
def addSpatialContainerSubscriber(event):
    createLocalSpatialCatalog(event.object)
    
    for ob in findObjectsProviding(event.object, IGeoreferenceable):
        utilities = tuple(getAllUtilitiesRegisteredFor(IIntIds, context=ob))
        if utilities: # assert that there are any utilites
            key = IKeyReference(ob, None)
            if key is not None:
                for utility in utilities:
                    utility.register(key)
        cat = get_catalog(ob)
        if cat is not None:
            id = getUtility(IIntIds, context=ob).getId(ob)
            cat.index_doc(id, ob)

def indexDocSubscriber(event):
    """A subscriber to IntIdAddedEvent"""
    ob = event.object
    cat = get_catalog(ob)
    if cat is not None:
        id = getUtility(IIntIds, context=ob).getId(ob)
        cat.index_doc(id, ob)

def reindexDocSubscriber(event):
    """A subscriber to ObjectModifiedEvent"""
    ob = event.object
    cat = get_catalog(ob)
    if cat is not None:
        id = getUtility(IIntIds, context=ob).queryId(ob)
        if id is not None:
            cat.index_doc(id, ob)

def unindexDocSubscriber(event):
    """A subscriber to IntIdRemovedEvent"""
    ob = event.object
    cat = get_catalog(ob)
    if cat is not None:
        id = getUtility(IIntIds, context=cat).queryId(ob)
        if id is not None:
            cat.unindex_doc(id)

@adapter(ILocation, IObjectRemovedEvent)
def removeIntIdSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in the local utility.
    """
    utilities = tuple(getAllUtilitiesRegisteredFor(IIntIds, context=ob))
    if utilities:
        key = IKeyReference(ob, None)
        # Register only objects that adapt to key reference
        if key is not None:
            # Notify the catalogs that this object is about to be removed.
            notify(IntIdRemovedEvent(ob, event))
            for utility in utilities:
                try:
                    utility.unregister(key)
                except KeyError:
                    pass

@adapter(ILocation, IObjectAddedEvent)
def addIntIdSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in the local id utilities and fires
    an event for the catalog.
    """
    utilities = tuple(getAllUtilitiesRegisteredFor(IIntIds, context=ob))
    if utilities: # assert that there are any utilites
        key = IKeyReference(ob, None)
        # Register only objects that adapt to key reference
        if key is not None:
            for utility in utilities:
                utility.register(key)
            # Notify the catalogs that this object was added.
            notify(IntIdAddedEvent(ob, event))

