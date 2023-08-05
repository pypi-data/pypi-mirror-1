import os
from zope.app.testing.functional import ZCMLLayer

SpatialIndexLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'SpatialIndexLayer', allow_teardown=True)

