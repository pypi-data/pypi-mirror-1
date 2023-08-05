from zope.formlib.form import EditForm, Fields
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')

from worldcookery.interfaces import ILocalKitchenTools
from worldcookery.browser.widget import DynamicSequenceWidget

class KitchenToolsEditForm(EditForm):
    form_fields = Fields(ILocalKitchenTools).omit('__parent__', '__name__')
    form_fields['kitchen_tools'].custom_widget = DynamicSequenceWidget
    label = _(u"Edit Kitchen Tools")

    template = NamedTemplate('worldcookery.form')