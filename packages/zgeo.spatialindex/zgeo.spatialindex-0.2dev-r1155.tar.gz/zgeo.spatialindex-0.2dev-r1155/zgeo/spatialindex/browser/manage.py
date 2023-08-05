import os
import sys

from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.spatialindex.interfaces import ISpatialIndex
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserView
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds


class IndexManage(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        rebuild = self.request.form.get('rebuild', None)
        if rebuild:
            self.rebuild()
            
    def rebuild(self):
        context = self.context
        index = ISpatialIndex(context)
        index.destroy()
        index = ISpatialIndex(context)
        intids = getUtility(IIntIds)
        for ob in context.values():
            try:
                intids.register(ob)
            except KeyError:
                pass
            index.add(ob)

    def count(self):
        index = ISpatialIndex(self.context)
        return len(index)

    def count_uids(self):
        intids = getUtility(IIntIds)
        return len(intids.refs)

    def name(self):
        return 'Spatial Index Management'

