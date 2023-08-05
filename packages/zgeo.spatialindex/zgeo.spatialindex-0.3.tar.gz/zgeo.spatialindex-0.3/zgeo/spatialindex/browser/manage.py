
from zope.event import notify
from zope.publisher.browser import BrowserView
from zgeo.spatialindex.site import get_catalog
from zgeo.spatialindex.interfaces import ISpatiallyCataloged
from zgeo.spatialindex.interfaces import IAddSpatialContainerEvent
from zgeo.spatialindex.event import addSpatialContainerSubscriber
from zgeo.spatialindex.event import AddSpatialContainerEvent


class CatalogManagement(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = get_catalog(self.context)
        rebuild = self.request.form.get('rebuild', None)
        if rebuild:
            self.rebuild()

    def rebuild(self):
        self.catalog.updateIndex(self.catalog['bounds'])

    def num_items(self):
        return len(self.catalog['bounds'].backward)


class SpatialCatalogCreator(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        docreate = self.request.get('create', None)
        if docreate:
            self.create()

    def create(self):
        addSpatialContainerSubscriber(AddSpatialContainerEvent(self.context))

    def created(self):
        created = False
        catalog = get_catalog(self.context)
        if catalog and ISpatiallyCataloged.providedBy(self.context):
            created = True
        return created

