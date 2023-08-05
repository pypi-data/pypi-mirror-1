
import os
from rtree import Rtree
from shapely.geometry import asShape

from zope.interface import implements
from zope.component import adapts
from persistent.dict import PersistentDict

from zope.annotation.interfaces import IAnnotations
from zgeo.geographer.interfaces import IGeoItem
from zgeo.spatialindex.interfaces import ISpatialIndex, ISpatiallyIndexable


class SpatialIndex(object):

    implements(ISpatialIndex)
    adapts(ISpatiallyIndexable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self._config = annotations.get('spatialindex.config', None)
        if not self._config:
            annotations['spatialindex.config'] = PersistentDict()
            self._config = annotations['spatialindex.config']
            #pathname = '.'.join(self.context.getPhysicalPath()[1:])
            name = "spatialindex-%s" % hash(repr(context)) # pathname
            self._config['name'] = name
            self._config['path'] = os.path.sep.join(
                [os.environ['CLIENT_HOME'], name]
                )
        self._idmap = annotations.get('spatialindex.idmap', None)
        if not self._idmap:
            annotations['spatialindex.idmap'] = PersistentDict()
            self._idmap = annotations['spatialindex.idmap']

    @property
    def _index(self):
        return Rtree(self._config['path'])

    @property
    def _records(self):
        return self._idmap

    def _recordize(self, item):
        if IGeoItem.providedBy(item):
            geom = asShape(item.__geo_interface__['geometry'])
            rec = (item.id, geom.bounds)
        elif isinstance(item, tuple):
            rec = item
        else:
            raise ValueError, "%s is not a valid index record" % item
        return rec

    def __len__(self):
        return len(self._records)

    def __iter__(self):
        return iter(self._idmap.values())

    def add(self, item):
        rec = self._recordize(item)
        intid = hash(rec[0])
        self._index.add(intid, rec[1])
        self._records[intid] = rec

    def remove(self, item):
        rec = self._recordize(item) 
        intid = hash(rec[0])
        self._index.delete(intid, self._records[intid][1])
        del self._records[intid]
        
    def intersects(self, bbox):
        for intid in self._index.intersection(bbox):
            yield self._records[intid]

    def destroy(self):
        name = self._config['name']
        annotations = IAnnotations(self.context)
        try:
            del annotations['spatialindex.config']
            del annotations['spatialindex.idmap']
        except:
            pass
        try:
            self._config = None
            self._idmap = None
            os.unlink(
                os.path.sep.join(
                    [os.environ['CLIENT_HOME'], '%s.dat' % name]
                    )
                )
            os.unlink(
                os.path.sep.join(
                    [os.environ['CLIENT_HOME'], '%s.idx' % name]
                    )
                )
        except:
            pass

