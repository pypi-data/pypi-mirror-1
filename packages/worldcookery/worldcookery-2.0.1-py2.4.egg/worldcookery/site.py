from zope.interface import implements
from zope.component import adapter
from zope.event import notify
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.component.site import SiteManagerContainer, LocalSiteManager

from worldcookery.interfaces import IWorldCookerySite
from worldcookery.interfaces import INewWorldCookerySiteEvent

class NewWorldCookerySiteEvent(object):
    implements(INewWorldCookerySiteEvent)

    def __init__(self, site):
        self.object = site

class WorldCookerySite(SiteManagerContainer, BTreeContainer):
    implements(IWorldCookerySite)

    def setSiteManager(self, sm):
        super(WorldCookerySite, self).setSiteManager(sm)
        notify(NewWorldCookerySiteEvent(self))

@adapter(IWorldCookerySite, IObjectAddedEvent)
def setSiteManagerWhenAdded(site, event):
    site.setSiteManager(LocalSiteManager(site))