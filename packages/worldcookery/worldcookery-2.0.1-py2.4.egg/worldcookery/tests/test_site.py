import unittest
from doctest import DocFileSuite

import zope.component.testing
import zope.component.eventtesting
from zope.app.component.hooks import setHooks
from worldcookery.site import setSiteManagerWhenAdded
from worldcookery.kitchentools import KitchenToolsFromFile
from worldcookery.kitchentools import createLocalKitchenTools

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    zope.component.provideUtility(KitchenToolsFromFile())
    zope.component.provideHandler(setSiteManagerWhenAdded)
    zope.component.provideHandler(createLocalKitchenTools)
    setHooks()

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('site.txt',
                     package='worldcookery',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')