import unittest
from doctest import DocTestSuite

def test_suite():
    return unittest.TestSuite((DocTestSuite('worldcookery.size'),))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')