import unittest
from doctest import DocFileSuite

import zope.component.testing
import zope.component.eventtesting
from zope.annotation.attribute import AttributeAnnotations
from worldcookery.rating import Rating

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)
    zope.component.provideAdapter(Rating)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('rating.txt',
                     package='worldcookery',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')