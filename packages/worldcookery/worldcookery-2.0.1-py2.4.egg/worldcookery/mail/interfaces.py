from zope.interface import Interface
from zope.schema import Tuple, TextLine
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery')

class IMailSubscriptions(Interface):

    subscribers = Tuple(
        title=_(u"Subscribers"),
        description=_(u"Email addresses of subscribers"),
        value_type=TextLine(title=_(u"Subscriber")),
        readonly=True
        )

    def subscribe(email):
        """Subscribe an email address to the notifications"""

    def unsubscribe(email):
        """Unsubscribe an email address"""