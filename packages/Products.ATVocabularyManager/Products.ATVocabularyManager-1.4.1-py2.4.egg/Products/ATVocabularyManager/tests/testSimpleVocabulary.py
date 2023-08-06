#
# Skeleton PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.testing import doctest
from Testing import ZopeTestCase
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase
from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

import common
common.installProducts()


class TestSimpleVocabulary(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        common.installWithinPortal(self.portal)
        self.atvm = common.getATVM(self.portal)

    def setupSimpleVocabularyContainer(self):
        self.setRoles(['Manager'])
        self.atvm.invokeFactory('SimpleVocabulary','svtest')
        self.atvm.svtest.setTitle('Test Vocabulary')

        
    def setupSimpleVocabulary(self):
        self.setupSimpleVocabularyContainer()
        self.atvm.svtest.invokeFactory('SimpleVocabularyTerm', 'key1')
        self.atvm.svtest.key1.setTitle('Value 1')
        self.logout()


    def testAddTerm(self):
        self.setupSimpleVocabularyContainer()
        svtest = self.atvm.svtest
        svtest.addTerm('foo','bar')
        self.assertEqual(svtest.foo.getVocabularyValue(), 'bar')
        # Test adding a term with a key that matches an attribute that
        # already exists via acquisition
        svtest.addTerm('author','Author')
        self.assertEqual(svtest.author.getVocabularyValue(), 'Author')

    def testImportCSVwoTitlerow(self):
        self.setupSimpleVocabularyContainer()
        csvdata= """\
"key1","value1"
"key2","value2"
"","value3"
"""
        svtest = self.atvm.svtest
        svtest.importCSV(csvdata)
        vocab=svtest.getVocabularyDict()

        # first both lines used?
        self.assertEqual(vocab['key1'],'value1')
        self.assertEqual(vocab['key2'],'value2')

        # there must be an Value value3 with a uuid as key
        for key in vocab.keys():
            if vocab[key] == 'value3':
                self.failUnless(key!="")


    def _createTestVocabulary(self):
        """creates a simplevocabulary for testing purposes
        using the utlity methods provided by atvocabularymanager
        """
        from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
        
        self.loginAsPortalOwner()
        testvocabs = {}
        testvocabs['teststates'] = (
            ('aut', u'Austria'),
            ('ger', u'Germany'),
            ('nor', u'Norway'),
            ('fin', u'Finland'))
            
        createSimpleVocabs(self.atvm, testvocabs)


    def testTranslations(self):
        """Test if SimpleVocabulary works with Linguaplone
        """
          
        self._createTestVocabulary()
        vocab = self.atvm.teststates
        # we need to install 'LinguaPlone' to translate
        # vocabularies
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        lpAvailable = qi.isProductAvailable('LinguaPlone')
        self.failUnless(lpAvailable, "Product LinguaPlone has to be available in INSTANCE_HOME")
        if not qi.isProductInstalled('LinguaPlone'):
            qi.installProduct('LinguaPlone')

  
        # translate some of our testvocabularies
        vocab.aut.setLanguage('en')
        vocab.aut.addTranslation('de', title='Oesterreich')       
        vocab.ger.setLanguage('en')
        vocab.ger.addTranslation('de', title='Deutschland')
        
        # a term and it's translation have to provide the same key
        aut = vocab.aut
        enKey = aut.getTermKey()
        deKey = aut.getTranslation('de').getTermKey()
        self.assertEqual(enKey, deKey, "translations don't provide the same key")

        # we can obtain the dictionary by providing an ``instance``
        # this instance's language is used to create the dictionary
        deDict = vocab.getVocabularyDict(vocab['aut-de'])
        self.assertEqual('Oesterreich', deDict[enKey], "Vocab Title is not translated")
        enDict = vocab.getVocabularyDict(vocab.aut)
        self.assertEqual('Austria', enDict[enKey])        
        
        # if ``instance`` is None, the vocabulary uses the
        # current language of the languagetool
        langtool = getToolByName(self.portal,'portal_languages')
        # set available portal languages
        langtool.supported_langs=['en', 'de']
        # per default english is the preferred language
        self.assertEqual('en', langtool.getPreferredLanguage())
        enDict = vocab.getVocabularyDict()
        # title for austria in english
        self.assertEqual('Austria', enDict[enKey])
        # switch to german
        vocab.REQUEST['set_language']='de'
        langtool.setLanguageBindings()
        self.assertEqual('de', langtool.getPreferredLanguage())
        deDict = vocab.getVocabularyDict()
        # dictionary has to return another title now
        self.assertEqual('Oesterreich', deDict[enKey], "Vocab Title is not translated")     
        

    def testGetTermKeyPath(self):
        """A SimpleVocabularyTerm simply returns a list containing it's key
        """
        
        self._createTestVocabulary()
        vocab = self.atvm.teststates
        self.assertEqual(['aut'], vocab.aut.getTermKeyPath())
        

        
def test_suite():
    from unittest import TestSuite, makeSuite
    optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
    
    suite = TestSuite()
    suite.addTest(makeSuite(TestSimpleVocabulary))
    
    suite.addTest(ZopeDocFileSuite('simplevocabulary.txt',
                                   optionflags=optionflags,
                                   package='Products.ATVocabularyManager.doc',
                                   test_class=TestSimpleVocabulary,
                                   ))
    
    return suite

if __name__ == '__main__':
    framework()
