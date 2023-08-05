from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros

class WorldCookeryMacros(BrowserView):

    template = ViewPageTemplateFile('worldcookery.pt')

    def __getitem__(self, key):
        return self.template.macros[key]

class StandardMacros(BaseMacros):
    macro_pages = ('worldcookery_macros',)