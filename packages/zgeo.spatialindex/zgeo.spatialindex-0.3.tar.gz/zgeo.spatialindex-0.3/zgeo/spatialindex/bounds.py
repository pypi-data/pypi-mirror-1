from zope.component import adapts
from zope.interface import implements
from zgeo.geographer.interfaces import IGeoreferenceable, IGeoreferenced
from zgeo.spatialindex.interfaces import IBounded
from shapely.geometry import asShape


class Bounded(object):

    """Provides a bounds attribute.
    
    Uses shapely to compute (minx, miny, maxx, maxy) bounding box of any
    georeferenced object.
    """

    implements(IBounded)
    adapts(IGeoreferenceable)

    def __init__(self, context):
        self.context = context

    @property
    def bounds(self):
        geo = IGeoreferenced(self.context)
        return asShape(
            {'type': geo.type, 'coordinates': geo.coordinates}
            ).bounds

