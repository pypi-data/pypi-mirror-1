from zope.interface import implements
from zope.component import adapts
from zope.size.interfaces import ISized
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from worldcookery.interfaces import IRecipe

class RecipeSize(object):
    """Provide size functionality for recipes

    For a demonstration of this adapter, consider the following
    recipe object, providing some demo data:

      >>> from worldcookery.recipe import Recipe
      >>> recipe = Recipe()
      >>> recipe.name = u"Fish and Chips"
      >>> recipe.ingredients = [u"Fish", u"Potato chips"]
      >>> recipe.description = u"Fish and Chips is a typical British dish."

    Now we instantiate the adapter.  For sorting, the adapter computes
    a recipe's size in the 'bytes' unit (number of characters):

      >>> size = RecipeSize(recipe)
      >>> size.sizeForSorting()
      ('byte', 71)

    It also provides a message id for displaying size in a UI.  In
    order to display the message correctly, we have to set up some
    basic services so we can use the translation facilities:

      >>> from zope.i18n import translate
      >>> translate(size.sizeForDisplay())
      u'71 characters'
    """
    implements(ISized)
    adapts(IRecipe)

    def __init__(self, context):
        self.context = context

    def sizeForSorting(self):
        """Compute a size for sorting"""
        chars = 0
        chars += len(self.context.name)
        chars += sum(map(len, self.context.tools))
        chars += sum(map(len, self.context.ingredients))
        chars += len(self.context.description)
        return ('byte', chars)

    def sizeForDisplay(self):
        """Generate a displayable size report"""
        unit, chars = self.sizeForSorting()
        return _('${chars} characters', mapping={'chars': chars})