from persistent import Persistent
from zope.interface import implements
from worldcookery.interfaces import IRecipe

class Recipe(Persistent):
    implements(IRecipe)

    __name__ = __parent__ = None

    name = u''
    ingredients = []
    tools = []
    time_to_cook = 0
    description = u''

from zope.component.factory import Factory
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')

recipeFactory = Factory(
    Recipe,
    title=_(u"Create a new recipe"),
    description = _(u"This factory instantiates new recipes.")
    )
