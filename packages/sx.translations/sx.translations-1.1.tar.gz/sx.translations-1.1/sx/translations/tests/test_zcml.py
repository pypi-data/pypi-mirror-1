# Copyright (c) 2006-2009 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
import os
import unittest

from zope.component.testing import PlacelessSetup
from zope.configuration import xmlconfig

from zope.component import queryUtility,getUtility
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import ILanguageAvailability
import sx.translations.tests

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        # create temp dir for .mo's
        self.context = xmlconfig.file('meta.zcml', sx.translations)

    def testRegisterTranslations(self):
        from sx.translations import Translations
        import zope.i18n.tests
        eq = self.assertEqual
        eq(queryUtility(ITranslationDomain), None)
        eq(queryUtility(ILanguageAvailability), None)
        xmlconfig.string(
            """<configure
            xmlns='http://namespaces.zope.org/zope'
            xmlns:i18n='http://namespaces.simplistix.co.uk/translations'>
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations locales="./locale2"/>
            </configure>
            </configure>""", self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale2', 'en',
                            'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        eq(util._catalogs, {'en': [unicode(path)]})
        util = getUtility(ILanguageAvailability, 'zope-i18n')
        result = util.getAvailableLanguages()
        result.sort()
        eq(result,[(u'en', None, None)])
        self.failUnless(isinstance(util,Translations))

    def testRegisterTranslationsMissing(self):
        from sx.translations import MissingTranslations
        import zope.i18n.tests
        eq = self.assertEqual
        eq(queryUtility(ITranslationDomain), None)
        eq(queryUtility(ILanguageAvailability), None)
        xmlconfig.string(
            """<configure
            xmlns='http://namespaces.zope.org/zope'
            xmlns:i18n='http://namespaces.simplistix.co.uk/translations'>
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations locales="./locale2"
                                       missing="./missing.pot"/>
            </configure>
            </configure>""", self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale2', 'en',
                            'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        eq(util._catalogs, {'en': [unicode(path)]})
        util = getUtility(ILanguageAvailability, 'zope-i18n')
        result = util.getAvailableLanguages()
        result.sort()
        eq(result,[(u'en', None, None)])
        self.failUnless(isinstance(util,MissingTranslations))
        eq(util.missing_path,
           os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                        'missing.pot'))
        eq(util.encoding,'utf-8')

    def testRegisterTranslationsMissingWithEncoding(self):
        from sx.translations import MissingTranslations
        import zope.i18n.tests
        eq = self.assertEqual
        eq(queryUtility(ITranslationDomain), None)
        eq(queryUtility(ILanguageAvailability), None)
        xmlconfig.string(
            """<configure
            xmlns='http://namespaces.zope.org/zope'
            xmlns:i18n='http://namespaces.simplistix.co.uk/translations'>
            <configure package="zope.i18n.tests">
            <i18n:registerTranslations locales="./locale2"
                                       missing="./missing.pot"
                                       encoding="ascii"/>
            </configure>
            </configure>""", self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale2', 'en',
                            'LC_MESSAGES', 'zope-i18n.mo')
        util = getUtility(ITranslationDomain, 'zope-i18n')
        eq(util._catalogs, {'en': [unicode(path)]})
        util = getUtility(ILanguageAvailability, 'zope-i18n')
        result = util.getAvailableLanguages()
        result.sort()
        eq(result,[(u'en', None, None)])
        self.failUnless(isinstance(util,MissingTranslations))
        eq(util.missing_path,
           os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                        'missing.pot'))
        eq(util.encoding,'ascii')

def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
