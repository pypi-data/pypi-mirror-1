import unittest
from zope.app.testing.functional import FunctionalDocFileSuite

def test_suite():
    return FunctionalDocFileSuite('README.txt')

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')