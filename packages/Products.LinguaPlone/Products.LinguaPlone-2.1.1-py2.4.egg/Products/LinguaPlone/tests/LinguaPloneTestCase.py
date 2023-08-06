from Testing import ZopeTestCase

# Make sure the dummy types are registered
from Products.LinguaPlone import examples
from Products.LinguaPlone.tests import dummy
ZopeTestCase.installProduct('LinguaPlone')

from Products.GenericSetup import EXTENSION, profile_registry

profile_registry.registerProfile('LinguaPlone_samples',
        'LinguaPlone example content types',
        'Extension profile including sample content types to test LinguaPlone',
        'profiles/sample_types',
        'Products.LinguaPlone',
        EXTENSION)
profile_registry.registerProfile('LinguaPlone_tests',
        'LinguaPlone test content types',
        'Extension profile including dummy types to test LinguaPlone',
        'profiles/test_types',
        'Products.LinguaPlone',
        EXTENSION)

from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import PloneTestCase
from Products.LinguaPlone.tests import utils
from Testing.ZopeTestCase.utils import setupCoreSessions

PORTAL_NAME = 'plone_ml'

@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    # Load the ZCML configuration for this package and its dependencies
    fiveconfigure.debug_mode = True


    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    PloneTestCase.installPackage('plone.browserlayer')
    fiveconfigure.debug_mode = False


setup_product()
PloneTestCase.setupPloneSite(id=PORTAL_NAME, 
        extension_profiles=['Products.LinguaPlone:LinguaPlone',
                            'Products.LinguaPlone:LinguaPlone_tests',
                            'Products.LinguaPlone:LinguaPlone_samples'])


class LinguaPloneTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_languages.use_cookie_negotiation=1
        self.portal.portal_languages.use_request_negotiation=1

    def getPortal(self):
        return self.app[PORTAL_NAME]

    def _setup(self):
        # Transparently extend the base setup
        PloneTestCase.PloneTestCase._setup(self)
        utils.setupGlobalRequest(self.app.REQUEST)
        setupCoreSessions(self.app)

    def addLanguage(self, language):
        self.portal.portal_languages.addSupportedLanguage(language)

    def setLanguage(self, language):
        request = self.app.REQUEST
        request['set_language'] = language
        self.portal.portal_languages.setLanguageBindings()


class LinguaPloneFunctionalTestCase(ZopeTestCase.Functional, LinguaPloneTestCase):
    pass

