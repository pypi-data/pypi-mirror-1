
import os
from rtree import Rtree
from shapely.geometry import asShape

from zope.interface import implements
from zope.component import adapts
from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations
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

    def _recordize(self, item):
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
        return iter(self._idmap.values())

    def add(self, id, ob):
        bounds = self._recordize(ob)
        intid = hash(id)
        self._index.add(intid, bounds)
        self._records[intid] = (id, bounds)

    def remove(self, id):
        intid = hash(id)
        self._index.delete(intid, self._records[intid][1])
        del self._records[intid]
        
    def intersects(self, bbox):
        for intid in self._index.intersection(bbox):
            yield self._records[intid]

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

