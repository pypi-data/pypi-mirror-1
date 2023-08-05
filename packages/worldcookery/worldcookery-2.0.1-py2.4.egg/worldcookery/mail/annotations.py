from persistent.list import PersistentList
from zope.interface import implements
from zope.event import notify
from zope.component import adapts
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from worldcookery.mail.interfaces import IMailSubscriptions

KEY = "worldcookery.subscriptions"

class MailSubscriptionAnnotations(object):           
    implements(IMailSubscriptions)
    adapts(IAnnotatable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        emails = annotations.get(KEY)
        if emails is None:
            emails = annotations[KEY] = PersistentList()
        self.emails = emails

    @property
    def subscribers(self):
        return tuple(self.emails)

    def subscribe(self, email):
        if email not in self.emails:
            self.emails.append(email)
            info = Attributes(IMailSubscriptions, 'subscribers')
            notify(ObjectModifiedEvent(self.context, info))

    def unsubscribe(self, email):
        if email in self.emails:
            self.emails.remove(email)
            info = Attributes(IMailSubscriptions, 'subscribers')
            notify(ObjectModifiedEvent(self.context, info))