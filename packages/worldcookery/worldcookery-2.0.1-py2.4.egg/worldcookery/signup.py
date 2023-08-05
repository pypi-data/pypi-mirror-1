from zope.interface import Interface, implements
from zope.schema import List, Choice
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal

class ISignup(Interface):

  signup_roles = List(
      title=_(u"Roles for new principals"),
      description=_(u"These roles will assigned to new principals."),
      value_type=Choice(vocabulary="Role Ids"),
      unique=True
      )

  def signUp(login, password, title):
      """Add a principal for yourself.  Returns the new principal's ID
      """

  def changePasswordTitle(login, password, title):
      """Change the principal's password and/or title.
      """

class SignupPrincipalFolder(PrincipalFolder):
    """Principal folder that allows users to sign up.
    """
    implements(ISignup)

    signup_roles = []

    def signUp(self, login, password, title):
        self[login] = InternalPrincipal(login, password, title)
        return self.__parent__.prefix + self.prefix + login

    def changePasswordTitle(self, login, password, title):
        if login not in self:
            raise ValueError("Principal is not managed by this "
                             "principal source.")
        principal = self[login]
        principal.password = password and password or principal.password
        principal.title = title and title or principal.title