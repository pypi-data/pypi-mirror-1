import unittest
import transaction
from zope.app.testing.functional import FunctionalDocFileSuite, getRootFolder
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from worldcookery.cookiecredentials import CookieCredentialsPlugin
from worldcookery.signup import SignupPrincipalFolder

def setUp(test):
    root = getRootFolder()

    # add and register PAU
    sm = root.getSiteManager()
    pau = sm['pau'] = PluggableAuthentication()
    sm.registerUtility(pau, IAuthentication)

    # add, configure and register cookie credentials plug-in
    cookies = pau['cookies'] = CookieCredentialsPlugin()
    cookies.loginpagename = 'wclogin.html'
    pau.credentialsPlugins = ('cookies',)

    # add, configure and register sign-up authenticator plug-in
    signups = pau['signups'] = SignupPrincipalFolder('worldcookery.signup.')
    signups.signup_roles = ['worldcookery.Visitor', 'worldcookery.Member']
    pau.authenticatorPlugins = ('signups',)

    # give anonymous user the visitor role
    role_manager = IPrincipalRoleManager(root)
    role_manager.assignRoleToPrincipal('worldcookery.Visitor', 'zope.anybody')

    transaction.commit()

def test_suite():
    return FunctionalDocFileSuite('signup.txt',
                                  package='worldcookery.browser',
                                  setUp=setUp)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
