#
# Language Independent Tests
#

from Products.LinguaPlone.tests import LinguaPloneTestCase
from Products.LinguaPlone.tests import dummy
from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation

from Products.CMFCore.utils import getToolByName


class TestLanguageIndependentFields(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        self.addLanguage('de')
        self.setLanguage('en')
        # Speed things up
        self.portal._delObject('portal_catalog')

    def testLanguageIndependentField(self):
        english = makeContent(self.folder, 'SimpleType', 'doc')
        english.setLanguage('en')

        contact = 'Fred Flintstone'
        english.setContactName(contact)
        german = makeTranslation(english, 'de')
        self.assertEqual(english.getContactName(), contact)
        self.assertEqual(english.getRawContactName(), contact)
        self.assertEqual(german.getContactName(), contact)
        self.assertEqual(german.getRawContactName(), contact)
        self.failUnless(english.contactName)
        self.failUnless(german.contactName)
        self.failUnless(hasattr(german, 'testing'))
        self.assertEqual(german.testing, english.contactName)
        self.assertEqual(english.contactName, german.contactName)

        contact = 'Barney Rubble'
        german.setContactName(contact)
        self.assertEqual(english.getContactName(), contact)
        self.assertEqual(english.getRawContactName(), contact)
        self.assertEqual(german.getContactName(), contact)
        self.assertEqual(german.getRawContactName(), contact)
        self.failUnless(english.contactName)
        self.failUnless(german.contactName)
        self.failUnless(hasattr(english, 'testing'))
        self.assertEqual(english.testing, german.contactName)
        self.assertEqual(english.contactName, german.contactName)

        # Sanity check: not all fields are language independent
        english.setTitle('English title')
        german.setTitle('German title')
        self.failIfEqual(english.Title(), german.Title())

    def testLinesField(self):
        english = makeContent(self.folder, 'SimpleType', 'doc')
        english.setLanguage('en')

        english.setLines(('foo', 'bar'))

        german = makeTranslation(english, 'de')
        self.assertEqual(german.getLines(), ('foo', 'bar'))

        english.setLines(('bar', 'baz'))
        self.assertEqual(german.getLines(), ('bar', 'baz'))

    def testReferenceFields(self):
        english = makeContent(self.folder, 'SimpleType', 'doc')
        english.setLanguage('en')
        german = makeTranslation(english, 'de')

        target = makeContent(self.folder, 'SimpleType', 'target')
        target.setLanguage('en')

        # Test language dependent reference fields
        english.setReferenceDependent(target.UID())
        self.assertEqual(english.getReferenceDependent().UID(), target.UID())
        self.assertEqual(german.getReferenceDependent(), None)

        # Test language independent reference fields
        english.setReference(target.UID())
        self.assertEqual(english.getReference().UID(), target.UID())
        self.assertEqual(german.getReference().UID(), target.UID())

        # Now we make a german translation of the target
        target_german = makeTranslation(target, 'de')

        # The language dependent field shouldn't change
        self.assertEqual(english.getReferenceDependent().UID(), target.UID())
        self.assertEqual(german.getReferenceDependent(), None)

        # It would be nice if the language independent field would now
        # point to the translation of the target, but this isn't easy to do
        # Neither the canonical or any translation of the content type with
        # the reference will actually be changed at this point. So we would
        # need to check on translation creation if the canonical is referenced
        # by any item and update those. This is a potential performance
        # nightmare, so we won't do it now
        self.assertEqual(english.getReference().UID(), target.UID())
        self.assertEqual(german.getReference().UID(), target.UID())

        # If we clear the reference, there should be no link left
        english.setReferenceDependent(None)
        english.setReference(None)

        self.assertEqual(english.getReferenceDependent(), None)
        self.assertEqual(german.getReferenceDependent(), None)

        self.assertEqual(english.getReference(), None)
        self.assertEqual(german.getReference(), None)

        # If the target already has a translation, it should set the reference
        # to the translation right away

        target2 = makeContent(self.folder, 'SimpleType', 'target2')
        target2_german = makeTranslation(target2, 'de')

        english.setReferenceDependent(target2.UID())
        self.assertEqual(english.getReferenceDependent().UID(), target2.UID())
        self.assertEqual(german.getReferenceDependent(), None)

        english.setReference(target2.UID())
        self.assertEqual(english.getReference().UID(), target2.UID())
        self.assertEqual(german.getReference().UID(), target2_german.UID())

        # If we delete the referenced item, it should no longer be referenced
        self.folder._delObject(target_german.getId())
        self.folder._delObject(target.getId())
        self.folder._delObject(target2_german.getId())
        self.folder._delObject(target2.getId())

        self.assertEqual(english.getReferenceDependent(), None)
        self.assertEqual(german.getReferenceDependent(), None)

        self.assertEqual(english.getReference(), None)
        self.assertEqual(german.getReference(), None)

    def testMultiValuedReferenceFields(self):
        english = makeContent(self.folder, 'SimpleType', 'doc')
        english.setLanguage('en')
        german = makeTranslation(english, 'de')

        target = makeContent(self.folder, 'SimpleType', 'target')
        target.setLanguage('en')
        target_german = makeTranslation(target, 'de')

        target2 = makeContent(self.folder, 'SimpleType', 'target2')
        target2.setLanguage('en')
        target2_german = makeTranslation(target2, 'de')

        # Test single valued
        english.setReferenceMulti(target.UID())
        self.assertEqual(english.getReferenceMulti()[0].UID(),target.UID())
        self.assertEqual(german.getReferenceMulti()[0].UID(),
            target_german.UID())

        # Test multi-valued
        english.setReferenceMulti([target.UID(), target2.UID()])
        self.assertEqual(set(english.getReferenceMulti()),
            set([target, target2]))
        self.assertEqual(set(german.getReferenceMulti()),
            set([target_german, target2_german]))

    def testBaseSchemaSetup(self):
        schema = dummy.SimpleType.schema
        self.assertEqual(schema['langIndependentInBase'].languageIndependent, 1)
        self.assertEqual(schema['langIndependentInDerived'].languageIndependent, 0)
        self.assertEqual(schema['langIndependentInBoth'].languageIndependent, 1)

    def testDerivedSchemaSetup(self):
        schema = dummy.DerivedType.schema
        self.assertEqual(schema['langIndependentInBase'].languageIndependent, 0)
        self.assertEqual(schema['langIndependentInDerived'].languageIndependent, 1)
        self.assertEqual(schema['langIndependentInBoth'].languageIndependent, 1)

    def testLangIndependentInBase(self):
        english = makeContent(self.folder, 'DerivedType', 'doc')
        english.setLanguage('en')
        german = makeTranslation(english, 'de')
        teststring = 'Test string'
        # When overriding languageIndependent from base class, the original
        # translation aware mutator actually checks for language independence
        english.setLangIndependentInBase(teststring)
        self.failIfEqual(german.getLangIndependentInBase(), teststring)
        self.failIfEqual(german.getRawLangIndependentInBase(), teststring)

    def testLangIndependentInDerived(self):
        english = makeContent(self.folder, 'DerivedType', 'doc')
        english.setLanguage('en')
        german = makeTranslation(english, 'de')
        teststring = 'Test string'
        # Note that you *can* override a 'false' languageIndependent field
        # from a base class...
        english.setLangIndependentInDerived(teststring)
        self.assertEqual(german.getLangIndependentInDerived(), teststring)
        self.assertEqual(german.getRawLangIndependentInDerived(), teststring)

    def testLangIndependentInBoth(self):
        english = makeContent(self.folder, 'DerivedType', 'doc')
        english.setLanguage('en')
        german = makeTranslation(english, 'de')
        teststring = 'Test string'
        english.setLangIndependentInBoth(teststring)
        self.assertEqual(german.getLangIndependentInBoth(), teststring)
        self.assertEqual(german.getRawLangIndependentInBoth(), teststring)

    # Test content that is not LP-aware
    def testLangIndependentGeneratedMethodsInNonLP(self):
        english = makeContent(self.folder, 'NonLPSimpleType', 'doc')
        english.setLanguage('en')
        teststring = 'Test string'
        # If this fails, you can't inherit unless you also get a copy of the schema
        english.setLangIndependentInBase(teststring)
        self.assertEqual(english.getLangIndependentInBase(), teststring)
        self.assertEqual(english.getRawLangIndependentInBase(), teststring)

    def testNotLangIndependentCustomMethodsInNonLP(self):
        english = makeContent(self.folder, 'NonLPSimpleType', 'doc')
        english.setLanguage('en')
        teststring = 'Test string'
        # If this fails, you can't inherit unless you also get a copy of the schema
        english.setFourthContactName(teststring)
        self.assertEqual(english.getFourthContactName(), 'getFourthContactName')
        self.assertEqual(str(english.contactName4), 'cn4 %s' % teststring)

    def testLangIndependentCustomMethodsInNonLP(self):
        english = makeContent(self.folder, 'NonLPSimpleType', 'doc')
        english.setLanguage('en')
        teststring = 'Test string'
        # If this fails, you can't inherit unless you also get a copy of the schema
        english.setFifthContactName(teststring)
        self.assertEqual(english.getFifthContactName(), 'getFifthContactName')
        # The original method is not detected properly... annotate?
        # Annotate the generated method!!!! provide original method name
        self.assertEqual(str(english.contactName5), 'cn5 %s' % teststring)

class TestLanguageIndependentCatalog(LinguaPloneTestCase.LinguaPloneTestCase):

    def afterSetUp(self):
        self.addLanguage('de')
        self.setLanguage('en')

    def testLangIndependentIndexing(self):
        catalog = getToolByName(self.folder, 'portal_catalog')
        catalog.addColumn('getContactName')
        
        english = makeContent(self.folder, 'SimpleType', 'doc')
        english.setLanguage('en')
        english.processForm(values=dict(contactName='foo'))
        res = [r.getContactName for r in
            catalog.unrestrictedSearchResults(portal_type='SimpleType')]
        self.assertEqual(res, ['foo'])
        
        german = makeTranslation(english, 'de')
        english.processForm(values=dict(contactName='bar'))
        res = [r.getContactName for r in
            catalog.unrestrictedSearchResults(portal_type='SimpleType')]
        self.assertEqual(res, ['bar', 'bar'])

def test_suite():
    import unittest, sys
    return unittest.findTestCases(sys.modules[__name__])
