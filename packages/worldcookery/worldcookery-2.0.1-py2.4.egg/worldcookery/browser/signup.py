from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from zope.exceptions.interfaces import UserError
from zope.security.proxy import removeSecurityProxy

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IPluggableAuthentication
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from worldcookery.signup import ISignup

class BaseSignUpView(BrowserView):

    def _signupfolder(self):
        pau = getUtility(IAuthentication)
        if not IPluggableAuthentication.providedBy(pau):
            raise LookupError("Signup requires a PAU instance.")

        for name, plugin in pau.getAuthenticatorPlugins():
            if ISignup.providedBy(plugin):
                return plugin

        raise TypeError("Signup requires a sign-up capable athenticator "
                        "plugin.")

class SignUpView(BaseSignUpView):

    signUpForm = ViewPageTemplateFile('signup.pt')

    def signUp(self, login, title, password, confirmation):
        if confirmation != password:
            raise UserError(_(u"Password and confirmation didn't match"))
        folder = self._signupfolder()
        if login in folder:
            raise UserError(_(u"This login has already been chosen."))
        principal_id = folder.signUp(login, password, title)

        role_manager = IPrincipalRoleManager(self.context)
        role_manager = removeSecurityProxy(role_manager)
        for role in folder.signup_roles:
            role_manager.assignRoleToPrincipal(role, principal_id)
        self.request.response.redirect("@@welcome.html")

class PasswordView(BaseSignUpView):

    changePasswordForm = ViewPageTemplateFile('password.pt')

    def changePassword(self, title, password=None, confirmation=None):
        if confirmation != password:
            raise UserError(_(u"Password and confirmation didn't match"))

        folder = self._signupfolder()
        pau = getUtility(IAuthentication)
        info = folder.principalInfo(self.request.principal.id[len(pau.prefix):])
        if info is None:
            raise UserError(_(u"Can only change the title and password "
                               "of users who signed up."))

        folder.changePasswordTitle(info.login, password, title)
        self.request.response.redirect(".")
