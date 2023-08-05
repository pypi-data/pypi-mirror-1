from zope.component import createObject, getMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

class ViewRecipe(BrowserPage):

    __call__ = ViewPageTemplateFile('recipeview.pt')

    def renderDescription(self):
        plaintext = createObject('zope.source.plaintext',
                                 self.context.description)
        view = getMultiAdapter((plaintext, self.request), name=u'')
        return view.render()

from zope.formlib.form import EditForm, AddForm, Fields, applyChanges
from zope.formlib.namedtemplate import NamedTemplate
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from worldcookery.interfaces import IRecipe
from worldcookery.browser.widget import DynamicSequenceWidget

class RecipeEditForm(EditForm):
    form_fields = Fields(IRecipe).omit('__parent__', '__name__')
    form_fields['ingredients'].custom_widget = DynamicSequenceWidget
    label = _(u"Edit recipe")

    template = NamedTemplate('worldcookery.form')

class RecipeAddForm(AddForm):
    form_fields = Fields(IRecipe).omit('__parent__', '__name__')
    form_fields['ingredients'].custom_widget = DynamicSequenceWidget
    label = _(u"Add recipe")

    template = NamedTemplate('worldcookery.form')

    def create(self, data):
        recipe = createObject(u'worldcookery.Recipe')
        applyChanges(recipe, self.form_fields, data)
        return recipe

form_template = NamedTemplateImplementation(
    ViewPageTemplateFile('form.pt'))
