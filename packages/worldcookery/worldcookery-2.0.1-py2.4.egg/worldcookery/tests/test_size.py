import unittest
from zope.i18n import translate
from worldcookery.recipe import Recipe
from worldcookery.size import RecipeSize

class RecipeSizeTestCase(unittest.TestCase):

    def setUp(self):
        self.recipe = recipe = Recipe()
        recipe.name = u"Fish and Chips"
        recipe.ingredients = [u"Fish", u"Potato chips"]
        recipe.description = u"Fish and Chips is a typical British dish."
        self.size = RecipeSize(recipe)

    def test_size_for_sorting(self):
        unit, size = self.size.sizeForSorting()
        self.assertEqual(unit, 'byte')
        self.assertEqual(size, 71)

    def test_size_for_display(self):
        msg = self.size.sizeForDisplay()
        self.assertEqual(u"71 characters", translate(msg))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RecipeSizeTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()