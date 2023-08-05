from zope.component.interfaces import ObjectEvent
from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from worldcookery.interfaces import IWorldCookerySite
from worldcookery.session import setUpClientIdAndSessionDataContainer

def evolve(context):
    """Setup client ID manager and session data container."""
    root = getRootFolder(context)
    for site in findObjectsProviding(root, IWorldCookerySite):
        sm = site.getSiteManager()
        if u'session_data' not in sm:
            setUpClientIdAndSessionDataContainer(ObjectEvent(site))