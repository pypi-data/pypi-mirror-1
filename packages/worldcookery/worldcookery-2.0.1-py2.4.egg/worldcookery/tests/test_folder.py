import unittest
from doctest import DocFileSuite, ELLIPSIS

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('folder.txt',
                     package='worldcookery',
                     optionflags=ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
