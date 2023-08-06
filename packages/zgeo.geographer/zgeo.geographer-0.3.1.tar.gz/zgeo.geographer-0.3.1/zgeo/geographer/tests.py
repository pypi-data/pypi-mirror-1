import unittest
from zope.testing import doctest
import zope.component.eventtesting
from zope.component import testing, provideAdapter
from zope.annotation.attribute import AttributeAnnotations
from zgeo.geographer.geo import GeoreferencingAnnotator

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def setUp(test):
    testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    provideAdapter(AttributeAnnotations)
    provideAdapter(GeoreferencingAnnotator)

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            package='zgeo.geographer',
            setUp=setUp,
            tearDown=testing.tearDown
            ),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
