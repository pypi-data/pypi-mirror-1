from zope.publisher.browser import BrowserView
from worldcookery.mail.interfaces import IMailSubscriptions

class MailSubscriptionView(BrowserView):

    def subscribe(self, email):
        subscriptions = IMailSubscriptions(self.context)
        subscriptions.subscribe(email)
        self.request.response.redirect('.')

    def unsubscribe(self, email):
        subscriptions = IMailSubscriptions(self.context)
        subscriptions.unsubscribe(email)
        self.request.response.redirect('.')