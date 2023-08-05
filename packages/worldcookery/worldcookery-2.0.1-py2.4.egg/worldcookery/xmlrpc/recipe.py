import time
import xmlrpclib
from zope.schema import getFields
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.publisher.xmlrpc import XMLRPCView
from worldcookery.interfaces import IRecipe

def to_unicode(string):
    if isinstance(string, unicode):
        return string
    return string.decode('utf-8')

class RecipeView(XMLRPCView):

    def info(self):
        return dict((field, getattr(self.context, field))
                    for field in getFields(IRecipe)
                    if field not in ('__parent__', '__name__'))

    def dublincore_info(self):
        dc = IZopeDublinCore(self.context)
        info = dict((field, getattr(dc, field))
                    for field in getFields(IZopeDublinCore))
        for name in ('effective', 'created', 'expires', 'modified'):
            if info[name]:
                epochtime = time.mktime(info[name].timetuple())
                info[name] = xmlrpclib.DateTime(epochtime)
            else:
                info[name] = ''
        return info

    def edit(self, info):
        context = self.context
        context.name = to_unicode(info['name'])
        context.ingredients = \
            [to_unicode(ingr) for ingr in info['ingredients']]
        context.tools = [to_unicode(tool) for tool in info['tools']]
        context.time_to_cook = info['time_to_cook']
        context.description = to_unicode(info['description'])

        return "Object updated successfully"