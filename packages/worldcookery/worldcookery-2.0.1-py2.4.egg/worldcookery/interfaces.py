from zope.interface import Interface
from zope.schema import List, Text, TextLine, Int, Choice
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.constraints import contains, containers

class IRecipe(IContained):
    """Store information about a recipe.
    """
    containers('worldcookery.interfaces.IRecipeContainer')

    name = TextLine(
        title=_(u"Name"),
        description=_(u"Name of the dish"),
        required = True
        )

    ingredients = List(
        title=_(u"Ingredients"),
        description=_(u"List of ingredients necessary for this recipe."),
        required=True,
        value_type=TextLine(title=_(u"Ingredient"))
        )

    tools = List(
        title=_(u"Tools"),
        description=_(u"List of necessary kitchen tools"),
        required=False,
        value_type=Choice(title=_(u"Tool"), vocabulary="Kitchen Tools"),
        unique=True
        )

    time_to_cook = Int(
        title=_(u"Time to cook"),
        description=_(u"Necessary time for preparing the meal described, "
                       "in minutes."),
        required=True
        )

    description = Text(
        title=_(u"Description"),
        description=_(u"Description of the recipe"),
        required=True
        )

from zope.schema import Float
from zope.annotation.interfaces import IAnnotatable

class IRatable(IAnnotatable):
    """Marker interface that promises that an implementing object maybe
    rated using ``IRating`` annotations.
    """

class IRating(Interface):
    """Give and query rating about objects, such as recipes.
    """

    def rate(rating):
        """Rate the current object with `rating`.
        """

    averageRating = Float(
        title=_(u"Average rating"),
        description=_(u"The average rating of the current object"),
        required=True
        )

    numberOfRatings = Int(
        title=_(u"Number of ratings"),
        description=_(u"The number of times the current has been rated"),
        required=True
        )

class IRecipeContainer(IContainer):
    contains('worldcookery.interfaces.IRecipe')

from zope.schema import Iterable

class IKitchenTools(Interface):

    kitchen_tools = Iterable(
        title=_(u"Kitchen tools"),
        description=_(u"A list of valid kitchen tools"),
        )

class ILocalKitchenTools(IKitchenTools, IContained):

    kitchen_tools = List(
        title=_(u"Kitchen tools"),
        description=_(u"A list of valid kitchen tools"),
        value_type=TextLine(title=_(u"Kitchen tool"))
        )

from zope.component.interfaces import IObjectEvent
from zope.app.component.interfaces import IPossibleSite

class IWorldCookerySite(IPossibleSite, IContainer):
    """Site containing the WorldCookery application"""

class INewWorldCookerySiteEvent(IObjectEvent):
    """Indicates that a new WorldCookery site has been created"""

import re
from zope.schema import ValidationError

class NotAnEmailAddress(ValidationError):
    __doc__ = _(u"This is not a valid email address")

regex = r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}"
check_email = re.compile(regex).match
def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True

class IMemberInfo(Interface):

    first = TextLine(
        title=_(u"First name"),
        required=True
        )

    last = TextLine(
        title=_(u"Last name"),
        required=True
        )

    email = TextLine(
        title=_(u"Email address"),
        required=False,
        constraint=validate_email
        )
