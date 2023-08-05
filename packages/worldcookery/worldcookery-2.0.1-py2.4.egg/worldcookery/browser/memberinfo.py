from zope.formlib.form import FormBase, Fields, haveInputWidgets
from zope.formlib.form import action, applyChanges, setUpEditWidgets
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from worldcookery.interfaces import IMemberInfo

class MemberInfoForm(FormBase):
    form_fields = Fields(IMemberInfo)
    label = _(u"Edit your member info")
    template = NamedTemplate('worldcookery.form')

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = setUpEditWidgets(
            self.form_fields, self.prefix, self.request.principal,
            self.request, adapters=self.adapters,
            ignore_request=ignore_request
            )

    @action(_(u"Save"), condition=haveInputWidgets)
    def handleSaveButton(self, action, data):
        principal = self.request.principal
        if applyChanges(principal, self.form_fields, data, self.adapters):
            self.status = _(u"Changes saved.")
        else:
            self.status = _(u"No changes.")