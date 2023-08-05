from zope.component.interfaces import ObjectEvent
from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from zope.app.intid import addIntIdSubscriber
from zope.app.catalog.catalog import indexDocSubscriber
from zope.app.component.site import setSite
from worldcookery.interfaces import IRecipe, IWorldCookerySite
from worldcookery.search import setupCatalogAndIndices

def evolve(context):
    """Setup catalog and indices for fulltext search."""
    root = getRootFolder(context)
    for site in findObjectsProviding(root, IWorldCookerySite):
        sm = site.getSiteManager()
        if u'catalog' not in sm:
            setupCatalogAndIndices(ObjectEvent(site))

            setSite(site)
            for recipe in findObjectsProviding(site, IRecipe):
                addIntIdSubscriber(recipe, ObjectEvent(recipe))
                indexDocSubscriber(ObjectEvent(recipe))
            setSite(None)