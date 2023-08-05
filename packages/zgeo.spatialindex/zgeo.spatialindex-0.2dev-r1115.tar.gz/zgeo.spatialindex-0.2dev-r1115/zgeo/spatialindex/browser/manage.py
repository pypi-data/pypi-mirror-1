import os
import sys

from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.spatialindex.interfaces import ISpatialIndex
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserView


class IndexManage(BrowserView):

    __name__ = 'manage-index'
   
    def __init__(self, context, request):
        self.context = context
        self.request = request
        rebuild = self.request.form.get('rebuild', 0)
        if rebuild:
            self.rebuild()
            
    def rebuild(self):
        """Request parameters are 'type' and 'coordinates'."""
        context = self.context
        request = self.request
        index = ISpatialIndex(context)
        index.destroy()
        index = ISpatialIndex(context)
        for id, item in context.items():
            index.add(id, IGeoreferenced(item))

    def count(self):
        index = ISpatialIndex(self.context)
        return len(index)

    def name(self):
        return 'Spatial Index Management'

