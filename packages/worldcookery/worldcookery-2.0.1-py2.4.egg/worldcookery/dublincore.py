from zope.component import adapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from worldcookery.interfaces import IRecipe

@adapter(IRecipe, IObjectModifiedEvent)
def updateRecipeDCTitle(recipe, event):
    """Update a recipe's Dublin Core Title property with its name

    Consider a simple recipe object with a name:

      >>> from worldcookery.recipe import Recipe
      >>> noodles = Recipe()
      >>> noodles.name = u"Noodles"

    In order for Dublin Core to work we need it to be annotatable:

      >>> from zope.interface import alsoProvides
      >>> from zope.annotation.interfaces import IAttributeAnnotatable
      >>> alsoProvides(noodles, IAttributeAnnotatable)

    It does not have a title yet:

      >>> dc = IWriteZopeDublinCore(noodles)
      >>> dc.title
      u''

    Now we send out the event and, voila!, the title has been set:

      >>> from zope.event import notify
      >>> from zope.lifecycleevent import ObjectModifiedEvent
      >>> notify(ObjectModifiedEvent(noodles))
      >>> dc = IWriteZopeDublinCore(noodles)
      >>> dc.title
      u'Noodles'
    """
    dc = IWriteZopeDublinCore(recipe)
    dc.title = recipe.name