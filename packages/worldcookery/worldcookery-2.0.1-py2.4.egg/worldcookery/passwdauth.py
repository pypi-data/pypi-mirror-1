from persistent import Persistent
from zope.interface import Interface, implements
from zope.schema import TextLine
from zope.location.interfaces import ILocation
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.principalfolder import PrincipalInfo

class IPasswd(Interface):

    prefix = TextLine(
        title=_(u"Prefix"),
        description=_(u"Prefix to be added to all principal IDs"),
        missing_value=u'',
        default=u'',
        readonly=True
        )

    filename = TextLine(
        title=_(u"File name"),
        description=_(u"Absolute path to the data file"),
        required=True
        )

class PasswdAuthenticator(Persistent):
    implements(IPasswd, IAuthenticatorPlugin, ILocation)
    __parent__ = __name__ = None

    def __init__(self, prefix=u'', filename=None):
        self.prefix = prefix
        self.filename = filename

    def _filedata(self):
        if self.filename is None:
            raise StopIteration
        for line in file(self.filename):
            yield line.strip().split(':', 3)

    def authenticateCredentials(self, credentials):
        if not (credentials and 'login' in credentials and
                'password' in credentials):
            return
        login, password = credentials['login'], credentials['password']
        for username, passwd, title in self._filedata():
            if (login, password) == (username, passwd):
                return PrincipalInfo(self.prefix+login, login,
                                     title, title)

    def principalInfo(self, id):
        if id.startswith(self.prefix):
            login = id[len(self.prefix):]
            for username, passwd, title in self._filedata():
                if login == username:
                    return PrincipalInfo(id, login, title, title)