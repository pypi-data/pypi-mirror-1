import os.path
from persistent import Persistent
from zope.interface import implements, alsoProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from worldcookery.interfaces import IKitchenTools, ILocalKitchenTools

class KitchenToolsFromFile(object):
    """Kitchen tools utility that reads data from a file
    """
    implements(IKitchenTools)

    @property
    def kitchen_tools(self):
        file_name = os.path.join(os.path.dirname(__file__), "kitchentools.dat")
        for line in file(file_name):
            if line.strip():
                yield line.strip().decode('utf-8')

class LocalKitchenTools(Persistent):
    """Local, persistent kitchen tools utility
    """
    implements(ILocalKitchenTools)

    __name__ = __parent__ = None

    kitchen_tools = []

def kitchenToolVocabulary(context):
    utility = getUtility(IKitchenTools)
    return SimpleVocabulary.fromValues(utility.kitchen_tools)
alsoProvides(kitchenToolVocabulary, IVocabularyFactory)

from zope.component import adapter
from worldcookery.interfaces import INewWorldCookerySiteEvent

@adapter(INewWorldCookerySiteEvent)
def createLocalKitchenTools(event):
    kitchentools = LocalKitchenTools()
    previous = getUtility(IKitchenTools)
    kitchentools.kitchen_tools = list(previous.kitchen_tools)

    sm = event.object.getSiteManager()
    sm['kitchentools'] = kitchentools
    sm.registerUtility(kitchentools, ILocalKitchenTools)
