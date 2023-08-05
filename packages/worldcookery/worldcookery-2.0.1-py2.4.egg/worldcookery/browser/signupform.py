from zope.formlib.form import AddForm, EditForm, Fields
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.app.authentication.principalfolder import IInternalPrincipalContainer

from worldcookery.signup import ISignup, SignupPrincipalFolder

class SignupAddForm(AddForm):
    form_fields = Fields(IInternalPrincipalContainer) + Fields(ISignup)
    label = _(u"Add signup principal folder")
    template = NamedTemplate('worldcookery.form')

    def create(self, data):
        folder = SignupPrincipalFolder(data['prefix'])
        folder.signup_roles = data['signup_roles']
        return folder

class SignupEditForm(EditForm):
    form_fields = Fields(ISignup)
    label = _(u"Configure signup principal folder")
    template = NamedTemplate('worldcookery.form')