import unittest
from doctest import DocTestSuite

import zope.component.testing
import zope.component.eventtesting
from zope.annotation.attribute import AttributeAnnotations
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from worldcookery.dublincore import updateRecipeDCTitle

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)
    zope.component.provideAdapter(ZDCAnnotatableAdapter,
                                  provides=IWriteZopeDublinCore)
    zope.component.provideHandler(updateRecipeDCTitle)

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('worldcookery.dublincore',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')