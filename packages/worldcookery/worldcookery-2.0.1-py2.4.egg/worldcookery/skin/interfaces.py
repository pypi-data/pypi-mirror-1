from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager

class IWorldCookerySkin(IDefaultBrowserLayer):
    """Skin for the WorldCookery application"""

class IHeaders(IViewletManager):
    """Viewlets for the HTML header"""

class IToolbar(IViewletManager):
    """Viewlets for the toolbar (e.g. tabs and actions)"""

class ISidebar(IViewletManager):
    """Viewlets for the sidebar (e.g. add menu)"""