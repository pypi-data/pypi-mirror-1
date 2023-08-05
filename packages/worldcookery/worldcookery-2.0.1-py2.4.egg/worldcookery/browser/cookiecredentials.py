from zope.formlib.form import EditForm, Fields
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.app.authentication.session import IBrowserFormChallenger

from worldcookery.cookiecredentials import ICookieCredentials

class CookieCredentialsEditForm(EditForm):
    form_fields = Fields(ICookieCredentials) + Fields(IBrowserFormChallenger)
    label = _(u"Configure cookie credentials plugin")
    template = NamedTemplate('worldcookery.form')