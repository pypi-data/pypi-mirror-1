from zope.component import adapter
from zope.app.session.http import ICookieClientIdManager
from zope.app.session.http import CookieClientIdManager
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.session import PersistentSessionDataContainer
from worldcookery.interfaces import INewWorldCookerySiteEvent

@adapter(INewWorldCookerySiteEvent)
def setUpClientIdAndSessionDataContainer(event):
    sm = event.object.getSiteManager()

    clientids = CookieClientIdManager()
    clientids.namespace = u'worldcookery'
    clientids.cookieLifetime = 3600
    sm['clientids'] = clientids
    sm.registerUtility(sm['clientids'], ICookieClientIdManager)

    session_data = PersistentSessionDataContainer()
    session_data.timeout = 3600
    session_data.resolution = 5
    sm['session_data'] = session_data
    sm.registerUtility(sm['session_data'], ISessionDataContainer)