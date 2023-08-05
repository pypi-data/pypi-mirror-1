from zope.component import getUtility, queryMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.dublincore.interfaces import IZopeDublinCore
from zope.index.text.interfaces import ISearchableText
from zope.traversing.browser import absoluteURL
from zope.app.catalog.interfaces import ICatalog
from zope.app.pagetemplate import ViewPageTemplateFile

class SearchPage(BrowserPage):

    def update(self, query):
        catalog = getUtility(ICatalog)
        self.results = catalog.searchResults(fulltext=query)

    render = ViewPageTemplateFile('search.pt')

    def __call__(self, query):
        self.update(query)
        return self.render()

    def getResultsInfo(self):
        for obj in self.results:
            icon = queryMultiAdapter((obj, self.request), name='zmi_icon')
            if icon is not None:
                icon = icon()

            title = None
            dc = IZopeDublinCore(obj, None)
            if dc is not None:
                title = dc.title

            text = ISearchableText(obj).getSearchableText()
            if len(text) > 100:
                text = text[:97] + u'...'

            yield {'icon': icon, 'title': title, 'text': text,
                   'absolute_url': absoluteURL(obj, self.request)}