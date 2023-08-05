
import os
from rtree import Rtree
from zope.interface import implements
from persistent.dict import PersistentDict
import persistent
from zope.index.interfaces import IInjection, IIndexSearch
from BTrees import IOBTree
from zope.traversing.api import getParent, getPath
from zope.app.catalog.attribute import AttributeIndex
from zope.app.container.contained import Contained
from zope.app.catalog.interfaces import ICatalogIndex

try:
    import zope.app.appsetup.product as zap
    INDEX_DIR = zap.getProductConfiguration('zgeo.spatialindex')['directory']
except:
    INDEX_DIR = os.environ['CLIENT_HOME']


class BaseIndex(persistent.Persistent):
    implements(IInjection, IIndexSearch)
    
    def __init__(self):
        name = "spatialindex-%s" % hash(repr(self))
        self._basepath = os.path.sep.join([INDEX_DIR, name])
        self.clear()

    def clear(self):
        self.backward = IOBTree.IOBTree()
        try:
            os.unlink('%s.dat' % self._basepath)
            os.unlink('%s.idx' % self._basepath)
        except:
            pass

    @property
    def rtree(self):
        return Rtree(self._basepath)

    def index_doc(self, docid, value):
        if docid in self.backward:
            self.unindex_doc(docid)
        self.backward[docid] = value
        self.rtree.add(docid, value)

    def unindex_doc(self, docid):
        value = self.backward.get(docid)
        if value is None:
            return
        self.rtree.delete(docid, value)
        del self.backward[docid]

    def apply(self, value):
        return self.rtree.intersection(value)


class BoundsIndex(AttributeIndex, BaseIndex, Contained):
    implements(ICatalogIndex)

