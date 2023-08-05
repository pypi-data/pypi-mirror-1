from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog import catalog


class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, uidutil):
        self.uids = uids
        self.uidutil = uidutil

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid in self.uids:
            obj = self.uidutil.getObject(int(uid))
            yield obj


class Catalog(catalog.Catalog):

    def searchResults(self, **searchterms):
        results = self.apply(searchterms)
        if results is not None:
            uidutil = getUtility(IIntIds, context=self)
            results = ResultSet(results, uidutil)
        return results

