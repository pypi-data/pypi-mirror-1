
from zope.interface import Interface, implements
from zgeo.spatialindex.site import get_catalog
from zope.publisher.browser import BrowserView


class ICatalogQueryView(Interface):

    def num_items():
        """Number of items in index."""

    def searchResults(**searchterms):
        """Return iterator over results."""

    def listResults(**searchterms):
        """Retults as a list."""


class CatalogQuery(BrowserView):
    implements(ICatalogQueryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = None

    def update(self):
        self.catalog = get_catalog(self.context)

    def num_items(self):
        """Number of items in index."""
        self.update()
        return len(self.index.backward)

    def parse_bbox(self, bbox=None):
        if bbox is None:
            b = self.request.form.get('bbox')
        else:
            b = bbox
        return tuple(float(x) for x in b.split(','))

    def searchResults(self, **searchterms):
        """Just like a catalog search."""
        self.update()
        return self.catalog.searchResults(**searchterms)

    def listResults(self, **searchterms):
        self.update()
        return list(self.catalog.searchResults(**searchterms))

    #def __call__(self):
    #    return repr(self)

