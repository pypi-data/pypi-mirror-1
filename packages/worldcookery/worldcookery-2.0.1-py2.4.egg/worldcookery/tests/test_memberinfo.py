import unittest
from doctest import DocFileSuite

import zope.component.testing

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('memberinfo.txt',
                     package='worldcookery',
                     setUp=zope.component.testing.setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')