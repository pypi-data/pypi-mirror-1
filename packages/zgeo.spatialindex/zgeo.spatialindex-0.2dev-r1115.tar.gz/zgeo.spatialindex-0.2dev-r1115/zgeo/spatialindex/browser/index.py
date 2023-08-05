
from zope.interface import Interface, implements
from zgeo.spatialindex.interfaces import ISpatialIndex

from zope.publisher.browser import BrowserView


class IIndexQueryView(Interface):

    def num_items():
        """Number of items in index."""

    def query(bounds=None):
        """Return iterator over records."""

    def list_query(bounds=None):
        """Return as a list."""


class IndexQuery(BrowserView):

    implements(IIndexQueryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def num_items(self):
        """Number of items in index."""
        index = ISpatialIndex(self.context)
        return len(index)

    def query(self, bounds=None):
        """Return iterator over the zope names of items."""
        index = ISpatialIndex(self.context)
        if not bounds:
            return iter(index)
        else:
            return index.intersects(bounds)

    def list_query(self, b=None):
        """Return as a list."""
        bounds = None
        if b:
            bounds = b
        else:
            bbox = self.request.form.get('bbox', None)
            if bbox:
                bounds = tuple(float(x) for x in bbox.split(','))
        index = ISpatialIndex(self.context)
        if not bounds:
            return list(index)
        else:
            return list(id for id in index.intersects(bounds))

