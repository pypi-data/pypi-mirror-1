from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.security.interfaces import IUnauthenticatedPrincipal

class LoginPage(BrowserPage):

    template = ViewPageTemplateFile('login.pt')

    def __call__(self):
        request = self.request
        if (not IUnauthenticatedPrincipal.providedBy(request.principal)
            and 'worldcookery.Login' in request):
            camefrom = request.get('camefrom', '.')
            request.response.redirect(camefrom)
        else:
            return self.template()