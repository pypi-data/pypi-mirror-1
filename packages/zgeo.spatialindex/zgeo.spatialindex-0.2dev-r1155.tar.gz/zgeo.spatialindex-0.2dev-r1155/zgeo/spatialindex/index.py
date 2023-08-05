
import os
from rtree import Rtree
from shapely.geometry import asShape

from zope.interface import implements
from zope.component import adapts, getUtility
from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.spatialindex.interfaces import ISpatialIndex, ISpatiallyIndexable

try:
    import zope.app.appsetup.product as zap
    INDEX_DIR = zap.getProductConfiguration('zgeo.spatialindex')['directory']
except:
    INDEX_DIR = os.environ['CLIENT_HOME']

CONFIG = "zgeo.spatialindex.config"
IDMAP = "zgeo.spatialindex.idmap"

class SpatialIndex(object):

    implements(ISpatialIndex)
    adapts(ISpatiallyIndexable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self._config = annotations.get(CONFIG, None)
        if not self._config:
            annotations[CONFIG] = PersistentDict()
            self._config = annotations[CONFIG]
            name = "spatialindex-%s" % hash(repr(context)) # pathname
            self._config['name'] = name
            self._config['path'] = os.path.sep.join([INDEX_DIR, name])
        self._idmap = annotations.get(IDMAP, None)
        if not self._idmap:
            annotations[IDMAP] = PersistentDict()
            self._idmap = annotations[IDMAP]

    @property
    def _index(self):
        return Rtree(self._config['path'])

    @property
    def _records(self):
        return self._idmap

    def _get_bounds(self, item):
        if IGeoreferenced.providedBy(item):
            return asShape(
                {'type': str(item.type), 'coordinates': item.coordinates}
                ).bounds
        elif isinstance(item, tuple):
            return item
        else:
            raise ValueError, "%s is not a valid index record" % item

    def __len__(self):
        return len(self._records)

    def __iter__(self):
        return iter(self._records.values())

    def add(self, ob, bounds=None):
        intids = getUtility(IIntIds)
        uid = intids.getId(ob)
        # Try two ways of getting the object's local name to store as
        # spatial index metadata
        try:
            oname = ob.__name__
        except:
            oname = ob.getId()
        if bounds:
            self._index.add(uid, bounds)
            self._records[uid] = (oname, bounds)
        else:
            geo = IGeoreferenced(ob)
            b = asShape({'type': geo.type, 'coordinates': geo.coordinates}).bounds
            self._index.add(uid, b)
            self._records[uid] = (oname, b)

    def remove(self, ob):
        intids = getUtility(IIntIds)
        uid = intids.getId(ob)
        self._index.delete(uid, self._records[uid][1])
        del self._records[uid]
        
    def intersects(self, bbox):
        intids = getUtility(IIntIds)
        for uid in self._index.intersection(bbox):
            yield self._records[uid]

    def destroy(self):
        name = self._config['name']
        annotations = IAnnotations(self.context)
        try:
            del annotations[CONFIG]
            del annotations[IDMAP]
        except:
            pass
        try:
            self._config = None
            self._idmap = None
            os.unlink(
                os.path.sep.join([INDEX_DIR, '%s.dat' % name])
                )
            os.unlink(
                os.path.sep.join([INDEX_DIR, '%s.idx' % name])
                )
        except:
            pass

