from zope.component import getSiteManager, queryUtility
from zope.interface import alsoProvides
from zope.app.component.site import LocalSiteManager
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.interfaces import ICatalog
from zgeo.spatialindex.index import BoundsIndex
from zgeo.spatialindex.interfaces import IBounded, ISpatiallyCataloged
from zgeo.spatialindex.catalog import Catalog
from zope.security.proxy import removeSecurityProxy
from zope.app.container.contained import ObjectAddedEvent


def createLocalSpatialCatalog(container):
    context = removeSecurityProxy(container)    
    try:
        context.setSiteManager(LocalSiteManager(context))
    except TypeError:
        pass
    sm = context.getSiteManager()
    if 'intids' not in sm:
        intids = IntIds()
        sm['intids'] = intids
        sm.registerUtility(intids, IIntIds)
    if 'catalog' not in sm:
        catalog = Catalog()
        sm['catalog'] = catalog
        sm.registerUtility(catalog, ICatalog)
        catalog['bounds'] = BoundsIndex('bounds', IBounded)
    alsoProvides(context, ISpatiallyCataloged)

def get_catalog(context):
    return queryUtility(ICatalog, context=context, default=None)
