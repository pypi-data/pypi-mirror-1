from zope.interface import implements
from zope.component import adapts
from zope.index.text.interfaces import ISearchableText
from worldcookery.interfaces import IRecipe

class RecipeSearchableText(object):
    """Extract searchable text from a recipe

    Consider a simple recipe with some data:

      >>> from worldcookery.recipe import Recipe
      >>> kashu_maki = Recipe()
      >>> kashu_maki.name = u'California roll'
      >>> kashu_maki.ingredients = [u'cucumber', u'avocado']
      >>> kashu_maki.description = u'The maki roll is made inside-out.'

    The searchable text only includes the name and the description,
    but not the ingredients:

      >>> RecipeSearchableText(kashu_maki).getSearchableText()
      u'California roll: The maki roll is made inside-out.'
    """
    implements(ISearchableText)
    adapts(IRecipe)

    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        return self.context.name + u': ' + self.context.description

from zope.component import adapter
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.text import TextIndex
from worldcookery.interfaces import INewWorldCookerySiteEvent

@adapter(INewWorldCookerySiteEvent)
def setupCatalogAndIndices(event):
    sm = event.object.getSiteManager()

    intids = IntIds()
    sm['intids'] = intids
    sm.registerUtility(intids, IIntIds)

    catalog = Catalog()
    sm['catalog'] = catalog
    sm.registerUtility(catalog, ICatalog)

    fulltext = TextIndex(
        interface=ISearchableText,
        field_name='getSearchableText',
        field_callable=True
        )
    catalog[u'fulltext'] = fulltext
