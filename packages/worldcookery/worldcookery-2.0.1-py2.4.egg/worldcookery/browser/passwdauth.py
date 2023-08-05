from zope.formlib.form import AddForm, EditForm, Fields
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')

from worldcookery.passwdauth import IPasswd, PasswdAuthenticator

class PasswdAddForm(AddForm):
    form_fields = Fields(IPasswd)
    label = _(u"Add passwd authenticator plugin")
    template = NamedTemplate('worldcookery.form')

    def create(self, data):
        return PasswdAuthenticator(**data)

class PasswdEditForm(EditForm):
    form_fields = Fields(IPasswd)
    label = _(u"Configure passwd authenticator plugin")
    template = NamedTemplate('worldcookery.form')