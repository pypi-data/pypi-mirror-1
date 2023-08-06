"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

# Let Zope know about the products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
from Products.PloneGetPaid.config import PLONE3
if not PLONE3:
    ZopeTestCase.installProduct('CMFonFive')
ZopeTestCase.installProduct('PloneGetPaid')



# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from Products.PloneGetPaid.tests.base import PloneGetPaidFunctionalTestCase
from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from Products.Five.testbrowser import Browser

# Set up a Plone site.

setupPloneSite()


def baseAfterSetUp( self ):
    """Code that is needed is the afterSetUp of both test cases.
    """

    # This looks like a safe place to install Five.
    ZopeTestCase.installProduct('Five')

    # XXX monkey patch everytime (until we figure out the problem where
    #   monkeypatch gets overwritten somewhere) 
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)
    except ImportError:
        # Not needed in Plone 3
        pass

    # Set up sessioning objects
    ZopeTestCase.utils.setupCoreSessions(self.app)

class WarehouseFunctionalTestCase(PloneGetPaidFunctionalTestCase):
    """Base class for functional integration tests for the warehouse product. 
    This may provide specific set-up and tear-down operations, or provide 
    convenience methods.
    """

    def afterSetUp( self ):
        super(WarehouseFunctionalTestCase,self).afterSetUp()
        self.portal.portal_quickinstaller.installProduct('PloneGetPaid')
        #Here we are setting Documents as shippeable
        options = IGetPaidManagementOptions(self.portal)
        options.shippable_types = ['Document']
        # Set browser and error handling
        self.browser = Browser()
        self.browser.handleErrors = False
