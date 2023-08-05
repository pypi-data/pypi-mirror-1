import unittest
from doctest import DocFileSuite

import zope.component.testing
from zope.filerepresentation.interfaces import IReadFile, \
    IWriteFile, IFileFactory

from worldcookery.interfaces import IRecipe
from worldcookery.filerepresentation import RecipeReadFile, \
    RecipeWriteFile, RecipeFactory, RecipeDirectoryFactory

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(RecipeReadFile)
    zope.component.provideAdapter(RecipeWriteFile)
    zope.component.provideAdapter(RecipeFactory)
    zope.component.provideAdapter(RecipeDirectoryFactory)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('filerepresentation.txt',
                     package='worldcookery',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')