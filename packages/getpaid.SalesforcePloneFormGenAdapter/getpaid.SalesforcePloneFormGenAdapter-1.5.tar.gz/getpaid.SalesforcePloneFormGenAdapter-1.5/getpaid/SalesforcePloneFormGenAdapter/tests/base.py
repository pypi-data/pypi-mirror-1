# Import the base test case classes
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.CMFPlone.tests import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.CMFCore.utils import getToolByName
import getpaid.SalesforcePloneFormGenAdapter

from Products.salesforcebaseconnector.tests import sfconfig   # get login/pw

from Products.PloneGetPaid.tests.base import PloneGetPaidFunctionalTestCase

# These must install cleanly, ZopeTestCase will take care of the others
ztc.installProduct('PloneFormGen')
ztc.installProduct('DataGridField')
ztc.installProduct('salesforcebaseconnector')
ztc.installProduct('salesforcepfgadapter')
ztc.installProduct('PloneGetPaid')

#ztc.installProduct('GetPaidPFGSalesforceAdapter')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['salesforcepfgadapter',
            'PloneGetPaid',
            'getpaid.SalesforcePloneFormGenAdapter',
            'getpaid.formgen']

@onsetup
def setupZCML():
    zcml.load_config('configure.zcml', getpaid.SalesforcePloneFormGenAdapter)
    ztc.installPackage('getpaid.SalesforcePloneFormGenAdapter')
    ztc.installPackage('getpaid.formgen')

setupZCML()
ptc.setupPloneSite(products=PRODUCTS)

class GetPaidPFGSalesforceAdapterTestCase(ptc.PloneTestCase):
    """Base class for integration tests for the 'GetPaidPFGSalesforceAdapter' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

class BaseGetPaidPFGSalesforceAdapterFunctionalTestCase(PloneGetPaidFunctionalTestCase):
    """Base class for functional doctests
    """
    def afterSetUp(self):
        PloneGetPaidFunctionalTestCase.afterSetUp(self)

        self.portal.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
        self.salesforce = getToolByName(self.portal, "portal_salesforcebaseconnector")
        self.salesforce.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list() # keep track of ephemeral test data to delete
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
    

# class FakeRequest(dict):

#     def __init__(self, **kwargs):
#         self.form = kwargs
