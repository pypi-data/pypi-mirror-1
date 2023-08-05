import unittest

from zope.i18n import translate
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('worldcookery_test')
from zope.publisher.browser import BrowserPage
from zope.app.testing.functional import BrowserTestCase

messages = {('es', u'msg'): u"Eso es un mensaje",
            ('de', u'msg'): u"Dies ist eine Nachricht"}
wc_test = SimpleTranslationDomain('worldcookery_test', messages)

class TestPage(BrowserPage):

    def __call__(self):
        msg = _(u'msg', u"This is a message")
        return translate(msg, context=self.request)

class LanguageAdapterTestCase(BrowserTestCase):

    def test_default(self):
        response = self.publish('/@@testpage')
        self.assertEqual(response.getBody(), u"This is a message")

    def test_http_header(self):
        response = self.publish('/@@testpage',
                                env={"HTTP_ACCEPT_LANGUAGE": 'de'})
        self.assertEqual(response.getBody(), u"Dies ist eine Nachricht")

    def test_browser_form(self):
        response = self.publish('/@@testpage', form={"ZopeLanguage": 'es'})
        self.assertEqual(response.getBody(), u"Eso es un mensaje")

    def test_form_overrides_header(self):
        response = self.publish('/@@testpage', form={"ZopeLanguage": 'es'},
                                env={"HTTP_ACCEPT_LANGUAGE": 'de'})
        self.assertEqual(response.getBody(), u"Eso es un mensaje")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LanguageAdapterTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()