from zope.interface import implements
from zope.component import adapts
from zope.exceptions.interfaces import UserError
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')

from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import NameChooser
from worldcookery.interfaces import IRecipeContainer

class RecipeFolder(BTreeContainer):
    implements(IRecipeContainer)

class RecipeNameChooser(NameChooser):
    adapts(IRecipeContainer)

    def checkName(self, name, object):
        if name != object.name:
            raise UserError(_(u"Given name and recipe name do not match!"))
        return super(RecipeNameChooser, self).checkName(name, object)

    def chooseName(self, name, object):
        name = object.name
        self.checkName(name, object)
        return name