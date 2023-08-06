## Copyright (c) 2006-2009 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
import unittest,os

from difflib import unified_diff
from sx.translations import Translations, MissingTranslations
from tempfile import mkstemp
from testfixtures import replace,test_datetime
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.interfaces import ILanguageAvailability
from zope.i18n.tests.test_translationdomain import \
     TestGlobalTranslationDomain,testdir
from zope.interface.verify import verifyObject

class TestTranslations(TestGlobalTranslationDomain):

    klass = Translations
    args = ('default',)
    
    def _getTranslationDomain(self):
        domain = self.klass(*self.args)
        path = testdir()
        en_catalog = GettextMessageCatalog('en', 'default',
                                           os.path.join(path, 'en-default.mo'))
        enGB_catalog = GettextMessageCatalog('en_GB', 'default',
                                             os.path.join(path, 'en-default.mo'))
        de_catalog = GettextMessageCatalog('de', 'default',
                                           os.path.join(path, 'de-default.mo'))

        domain.addCatalog(en_catalog)
        domain.addCatalog(enGB_catalog)
        domain.addCatalog(de_catalog)
        return domain

    # test that we implement ILanguageAvailability
    # funny names is so we don't hide the test from TestGlobalTranslationDomain
    def testILAInterface(self):
        verifyObject(ILanguageAvailability, self._domain)

    def testGetAvailableLanguages(self):
        self.assertEqual(self._domain.getAvailableLanguages(),
                         [
            ('de',None,None),
            ('en',None,None),
            ('en','GB',None),
            ])

def sx_testdir():
    from sx.translations import tests
    return os.path.dirname(tests.__file__)

class TestMissingTranslations(TestTranslations):

    klass = MissingTranslations

    def setUp(self):
        fd,path = mkstemp('.pot')
        os.close(fd) # or tests fubar on Windoze
        self.path = path
        self.args = ('default',['en'],path)
        super(TestMissingTranslations,self).setUp()
        
    def tearDown(self):
        super(TestMissingTranslations,self).tearDown()
        os.remove(self.path)

    def _compare(self,path_a,path_b):
        a = open(path_a).readlines()
        b = open(path_b).readlines()
        result = ''.join(unified_diff(a,b,path_a,path_b))
        if result:
            self.fail('\n'+result)
        
    @replace('sx.translations.datetime',test_datetime())
    def testTranslateUnknown(self):
        self._domain.translate('spanner')
        self._compare(
            os.path.join(sx_testdir(),'spanner.pot'),
            self.path,
            )
                 
    def testTranslateUnknownAlreadySeen(self):
        s_path = os.path.join(sx_testdir(),'spanner.pot')
        f = open(self.path,'w')
        f.write(open(s_path).read())
        f.close()
        # we re-create the domain to load the filled .pot file
        domain =  self._getTranslationDomain()
        domain.translate('spanner')
        self._compare(
            s_path,
            self.path,
            )

    def testMessageIDRecursiveTranslate(self):
        # MissingTranslations doesn't support recursive translation.
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTranslations))
    suite.addTest(unittest.makeSuite(TestMissingTranslations))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

