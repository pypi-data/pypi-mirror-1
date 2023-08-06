"""Base testing infrastructure
"""

import os

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from utils import MockMailHost

test_home = os.path.dirname(__file__)

PRODUCTS = ['CMFPlacefulWorkflow',
            'ATBackRef',
            'ATExtensions',
            'DigestoContentTypes']

for product in PRODUCTS:
   ztc.installProduct(product)

@onsetup
def setup_digesto_content_types():
    """Set up the environment to test the DigestoContentTypes product.
    """

    fiveconfigure.debug_mode = True
    import Products.DigestoContentTypes
    zcml.load_config('configure.zcml', Products.DigestoContentTypes)
    fiveconfigure.debug_mode = False

    ztc.installPackage('iw.fss')


setup_digesto_content_types()
ptc.setupPloneSite(products=PRODUCTS+['iw.fss'])

class DigestoContentTypesTestCase(ptc.PloneTestCase):
    """Base class for all the tests in this package"""

class DigestoContentTypesFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for all functional tests in this package"""

    def afterSetUp(self):
        # Use the fake mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost('MailHost')

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost

    def setUp(self):
        super(ptc.FunctionalTestCase, self).setUp()
        from Products.DigestoContentTypes.utilities.interfaces import \
            INormativaTypes
        from Products.DigestoContentTypes.utilities.types import NormativaTypes

        sm = self.portal.getSiteManager()
        if not sm.queryUtility(INormativaTypes):
            sm.registerUtility(NormativaTypes(),
                                INormativaTypes)
            nt = sm.getUtility(INormativaTypes)
            nt.types = [u'Ley', u'Ordenanza', u'Decreto',
                        unicode('Resolución','utf-8')]
