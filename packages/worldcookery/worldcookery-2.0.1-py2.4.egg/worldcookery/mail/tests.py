import unittest
from doctest import DocFileSuite, ELLIPSIS

import zope.component.testing
import zope.component.eventtesting
from zope.interface import implements
from zope.sendmail.interfaces import IMailDelivery
from zope.annotation.attribute import AttributeAnnotations

from worldcookery.mail.recipe import notifyModified
from worldcookery.mail.annotations import MailSubscriptionAnnotations

class DummyMailDelivery(object):
    implements(IMailDelivery)
    def send(self, fromaddr, toaddr, msg):
        print msg

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)
    zope.component.provideAdapter(MailSubscriptionAnnotations)
    zope.component.provideUtility(DummyMailDelivery(), name='worldcookery')
    zope.component.provideHandler(notifyModified)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('emailsubscriptions.txt',
                     setUp=setUp,
                     tearDown=zope.component.testing.tearDown,
                     optionflags=ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')