from zope.interface import implements
from zope.component import adapts
from zope.filerepresentation.interfaces import IReadFile, IWriteFile
from zope.filerepresentation.interfaces import IFileFactory
from worldcookery.recipe import Recipe
from worldcookery.interfaces import IRecipe

class RecipeReadFile(object):
    implements(IReadFile)
    adapts(IRecipe)

    def __init__(self, context):
        self.context = context
        self.data = self.context.description.encode('utf-8')

    def read(self):
        return self.data

    def size(self):
        return len(self.data)

class RecipeWriteFile(object):
    implements(IWriteFile)
    adapts(IRecipe)

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.description = data.decode('utf-8')

from worldcookery.interfaces import IRecipeContainer

class RecipeFactory(object):
    implements(IFileFactory)
    adapts(IRecipeContainer)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        recipe = Recipe()
        recipe.name = name.title()
        recipe.description = data.decode('utf-8')
        return recipe

from zope.filerepresentation.interfaces import IDirectoryFactory
from zope.exceptions.interfaces import UserError

class RecipeDirectoryFactory(object):
    implements(IDirectoryFactory)
    adapts(IRecipeContainer)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        raise UserError(u"Cannot create subfolders in recipe folders.")

