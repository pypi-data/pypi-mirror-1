import email.Charset
email.Charset.add_charset('utf-8', email.Charset.SHORTEST, None, None)
from datetime import datetime
from email.MIMEText import MIMEText

from zope.component import getUtility, adapter
from zope.sendmail.interfaces import IMailDelivery
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent

from worldcookery.interfaces import IRecipe
from worldcookery.mail.interfaces import IMailSubscriptions

@adapter(IRecipe, IObjectAddedEvent)
def notifyAdded(recipe, event):
    return emailNotifications(recipe, "added")

@adapter(IRecipe, IObjectModifiedEvent)
def notifyModified(recipe, event):
    return emailNotifications(recipe, "modified")

@adapter(IRecipe, IObjectRemovedEvent)
def notifyRemoved(recipe, event):
    return emailNotifications(recipe, "removed")

def _messageBody(recipe):
    body = u"""Name: %(name)s

Time to cook: %(time_to_cook)s

Ingredients:
%(ingredients)s

Necessary Kitchen Tools:
%(tools)s

%(description)s"""
    return body % {
        'name': recipe.name,
        'time_to_cook': recipe.time_to_cook,
        'ingredients': '\n'.join(u'- ' + ingr for ingr in recipe.ingredients),
        'tools': '\n'.join(u'- ' + tool for tool in recipe.tools),
        'description': recipe.description
        }

def emailNotifications(recipe, action):
    subscriptions = IMailSubscriptions(recipe, None)
    if subscriptions is None or not subscriptions.subscribers:
        return
    subject = "'%s' was %s" % (recipe.name, action)
    message = MIMEText(_messageBody(recipe).encode('utf-8'), 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = 'notify@worldcookery.com'
    message['To'] = ', '.join(subscriptions.subscribers)
    message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    mailer = getUtility(IMailDelivery, 'worldcookery')
    mailer.send("notify@worldcookery.com", subscriptions.subscribers,
                message.as_string())