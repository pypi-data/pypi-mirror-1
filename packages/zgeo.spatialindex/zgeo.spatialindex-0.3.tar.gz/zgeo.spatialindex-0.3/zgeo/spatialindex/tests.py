import unittest
from zope.testing import doctest
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.component import provideAdapter
from zgeo.geographer.geo import GeoreferencingAnnotator
from zgeo.spatialindex.bounds import Bounded
from zgeo.spatialindex.testing import SpatialIndexLayer

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def setUp(test):
    placefulSetUp()
    provideAdapter(GeoreferencingAnnotator)
    provideAdapter(Bounded)
    import os
    os.environ['CLIENT_HOME'] = os.getcwd()

def tearDown(test):
    placefulTearDown()

def test_suite():
    views = FunctionalDocFileSuite(
            'catalog-views.txt',
            optionflags=optionflags,
            )
    views.layer = SpatialIndexLayer

    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            package='zgeo.spatialindex',
            setUp=setUp,
            tearDown=tearDown,
            optionflags=optionflags,
            ),
        views,
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
