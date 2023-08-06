""" 
    An adapter for PloneFormGen that saves submitted form data
    to Salesforce.com after it is run through GetPaid's workflow
"""

__author__  = ''
__docformat__ = 'plaintext'

# Python imorts
import logging

# Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from zope.interface import classImplements
from DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
try:
    # 3.0+
    from zope.contenttype import guess_content_type
except ImportError:
    # 2.5
    from zope.app.content_types import guess_content_type

# CMFCore
from Products.CMFCore.Expression import getExprContext

# Plone imports
from Products.CMFPlone.utils import safe_hasattr
from Products.Archetypes.public import StringField, SelectionWidget, \
    DisplayList, Schema, ManagedSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

# DataGridField
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.DataGridField import FixedRow

# Interfaces
from Products.PloneFormGen.interfaces import IPloneFormGenField

# PloneFormGen imports
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

# Local imports
from getpaid.SalesforcePloneFormGenAdapter.config import PROJECTNAME, REQUIRED_MARKER, SF_ADAPTER_TYPES
from getpaid.SalesforcePloneFormGenAdapter import SalesforcePloneFormGenAdapterMessageFactory as _
from getpaid.SalesforcePloneFormGenAdapter import HAS_PLONE25, HAS_PLONE30

from Products.salesforcepfgadapter.content.salesforcepfgadapter import SalesforcePFGAdapter

if HAS_PLONE25:
    import zope.i18n

# Get Paid events
from getpaid.core.interfaces import workflow_states, IShoppingCartUtility
from zope.app.component.hooks import getSite
from zope.app.annotation.interfaces import IAnnotations


logger = logging.getLogger("GetPaidPFGSalesforce")

schema = FormAdapterSchema.copy() + Schema((
    StringField('SFObjectType',
        searchable=0,
        required=1,
        read_permission=ModifyPortalContent,
        default=u'Contact',
        mutator='setSFObjectType',
        widget=SelectionWidget(
            label='Salesforce Object Type',
            i18n_domain = "getpaidpfgsalesforceadapter",
            label_msgid = "label_salesforce_type_text",
            ),
        vocabulary='displaySFObjectTypes',
        ),
    DataGridField('fieldMap',
         searchable=0,
         required=1,
         read_permission=ModifyPortalContent,
         schemata='field mapping',
         columns=('field_path', 'form_field', 'sf_field'),
         fixed_rows = "generateFormFieldRows",
         allow_delete = False,
         allow_insert = False,
         allow_reorder = False,
         widget = DataGridWidget(
             label='Form fields to Salesforce fields mapping',
             label_msgid = "label_salesforce_field_map",
             description="""The following Form Fields are available\
                 within your Form Folder. Choose the appropriate \
                 Salesforce Field for each Form Field.""",
             description_msgid = 'help_salesforce_field_map',
             columns= {
                 "field_path" : FixedColumn("Form Fields (path)", visible=False),
                 "form_field" : FixedColumn("Form Fields"),
                 "sf_field" : SelectColumn("Salesforce Fields", 
                                           vocabulary="buildSFFieldOptionList")
             },
             i18n_domain = "getpaidpfgsalesforceadapter",
             ),
        ),
    DataGridField('getPaidFieldMap',
         searchable=0,
         required=1,
         read_permission=ModifyPortalContent,
         schemata='field mapping',
         columns=('field_path', 'form_field', 'sf_field'),
         fixed_rows = "generateGetPaidFormFieldRows",
         allow_delete = False,
         allow_insert = False,
         allow_reorder = False,
         widget = DataGridWidget(
             label='Get Paid fields to Salesforce fields mapping',
             label_msgid = "label_salesforce_getpaid_field_map",
             description="""The following Form Fields are provided\
                 by the GetPaid order. Choose the appropriate \
                 Salesforce Field for each Form Field.""",
             description_msgid = 'help_salesforce_getpaid_field_map',
             columns= {
                 "field_path" : FixedColumn("Form Fields (path)", visible=False),
                 "form_field" : FixedColumn("GetPaid Fields"),
                 "sf_field" : SelectColumn("Salesforce Fields", 
                                           vocabulary="buildSFFieldOptionList")
             },
             i18n_domain = "getpaidpfgsalesforceadapter",
             ),
        )
))

# move 'field mapping' schemata before the inherited overrides schemata
schema = ManagedSchema(schema.copy().fields())
schema.moveSchemata('field mapping', -1)

class GetPaidPFGSalesforceAdapter(SalesforcePFGAdapter):
    """ An adapter for PloneFormGen that saves results to Salesforce
    after GetPaid's workflow executes.
    """
    schema = schema
    security = ClassSecurityInfo()
    
    if not HAS_PLONE30:
        finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
    
    meta_type = portal_type = 'GetPaidPFGSalesforceAdapter'
    archetype_name = 'Salesforce Adapter'
    content_icon = 'salesforce.gif'
    
    def initializeArchetype(self, **kwargs):
        """Initialize Private instance variables
        """
        FormActionAdapter.initializeArchetype(self, **kwargs)
        
        # All Salesforce fields for the current Salesforce object type. Since
        # we need this for every row in our field mapping widget, it's better
        # to just set it on the object when we set the Salesforce object type. 
        # This way we don't query Salesforce for every field on our form.
        self._fieldsForSFObjectType = {}

        #
        # Verify Products.Salesforcebaseconnector is installed
        #
        sfbc = getattr(self, 'portal_salesforcebaseconnector', None)
        if sfbc is None:
            self.plone_utils.addPortalMessage(_(u'There does not appear to be an installed Salesforce Base Connector.  This adapter will not function without one so please install and configure before using the GetPaid Salesforce adapter.'), "warning")

            # I have been unable to get the message to show up with this redirect in place.
#            self.REQUEST.RESPONSE.redirect(self.REQUEST['HTTP_REFERER'])

          
    security.declareProtected(View, 'onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """ The essential method of a PloneFormGen Adapter:
        - collect the submitted form data
        - examine our field map to determine which Saleforce fields
          to populate
        - if there are any mappings, store them as an annotation on
          the cart
        """
        logger.info('Calling onSuccess()')

        scu = zope.component.getUtility(IShoppingCartUtility)
        cart = scu.get(self, create=True)

        if (cart == None):
            logger.info("Unable to get cart")
        else:
            # Ideally I'd want to associate this with the item, but I have no guarentee that
            # it has been created at this point.  It all depends on the order the adapters run.
            annotation = IAnnotations(cart)
            annotation["getpaid.SalesforcePloneFormGenAdapter.added"] = 1

            sObject = self._buildSObjectFromForm(fields, REQUEST)
            annotation["getpaid.SalesforcePloneFormGenAdapter.GetPaidSFMapping"] = self.getPaidFieldMap
            annotation["getpaid.SalesforcePloneFormGenAdapter.sObject"] = sObject
   
    security.declareProtected(ModifyPortalContent, 'setSFObjectType')
    def setSFObjectType(self, newType):
        """When we set the Salesforce object type,
           we also need to reset all the possible fields
           for our mapping selection menus.
        """
        logger.debug('Calling setSFObjectType()')
        
        def _purgeInvalidMapping(fname):
            accessor = getattr(self, self.Schema().get(fname).accessor)
            mutator = getattr(self, self.Schema().get(fname).mutator)
            
            eligible_mappings = []
            for mapping in accessor():
                if mapping.has_key('sf_field') and not \
                  self._fieldsForSFObjectType.has_key(mapping['sf_field']):
                    continue
                
                eligible_mappings.append(mapping)
            
            mutator(tuple(eligible_mappings))
        
        # set the SFObjectType
        self.SFObjectType = newType
        
        # clear out the cached field info
        self._fieldsForSFObjectType = self._querySFFieldsForType()
        
        # purge mappings that are no longer valid
        _purgeInvalidMapping('fieldMap')

    security.declareProtected(ModifyPortalContent, 'generateGetPaidFormFieldRows')
    def generateGetPaidFormFieldRows(self):
        """This method returns a list of rows for the field mapping
           ui. One row is returned for each field on the GetPaid order.
        """
        fixedRows = []

        #
        # First and last name are calculated fields created by splitting contact_information.name
        #
   
        # First Name
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "First Name", 
                                               "field_path" : "contact_information,first_name",
                                               "sf_field" : ""}))
        # Last Name
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Last Name", 
                                               "field_path" : "contact_information,last_name",
                                               "sf_field" : ""}))
        # Phone Number
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Phone Number", 
                                               "field_path" : "contact_information,phone_number",
                                               "sf_field" : ""}))
        # Email
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Email", 
                                               "field_path" : "contact_information,email",
                                               "sf_field" : ""}))
        # Contact?
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Contact Allowed", 
                                               "field_path" : "contact_information,marketing_preference",
                                               "sf_field" : ""}))
        # Email HTML
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Email Format Preference", 
                                               "field_path" : "contact_information,email_html_format",
                                               "sf_field" : ""}))

        # Billing Address
        # Address lines are combined since salesforce only has one line for it
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address Street", 
                                               "field_path" : "billing_address,bill_address_street",
                                               "sf_field" : ""}))
        # 	City
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address City", 
                                               "field_path" : "billing_address,bill_city",
                                               "sf_field" : ""}))
        # 	Country
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address Country", 
                                               "field_path" : "billing_address,bill_country",
                                               "sf_field" : ""}))

        # 	State
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address State", 
                                               "field_path" : "billing_address,bill_state",
                                               "sf_field" : ""}))
        # 	Zip
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address Zip", 
                                               "field_path" : "billing_address,bill_postal_code",
                                               "sf_field" : ""}))
        # Shipping Address
        # Address lines are combined since salesforce only has one line for it
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address Street", 
                                               "field_path" : "shipping_address,ship_address_street",
                                               "sf_field" : ""}))
        # 	City
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address City", 
                                               "field_path" : "shipping_address,ship_city",
                                               "sf_field" : ""}))
        # 	Country
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address Country", 
                                               "field_path" : "shipping_address,ship_country",
                                               "sf_field" : ""}))

        # 	State
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address State", 
                                               "field_path" : "shipping_address,ship_state",
                                               "sf_field" : ""}))
        # 	Zip
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address Zip", 
                                               "field_path" : "shipping_address,ship_postal_code",
                                               "sf_field" : ""}))
 
        # Order Id
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Order Id", 
                                               "field_path" : "order_id",
                                               "sf_field" : ""}))
        # Order Date
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Creation Date", 
                                               "field_path" : "created_date",
                                               "sf_field" : ""}))
        # Total Price
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Total", 
                                               "field_path" : "getTotalPrice",
                                               "sf_field" : ""}))

        # Transaction Id
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Transaction Id", 
                                               "field_path" : "processor_order_id",
                                               "sf_field" : ""}))
        # Credit Card Last 4
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "CC Last 4", 
                                               "field_path" : "user_payment_info_last4",
                                               "sf_field" : ""}))

        # 
        # Line Items:
        #      Quantity
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Quantity", 
                                               "field_path" : "shopping_cart,items,quantity",
                                               "sf_field" : ""}))
        #      Item Id
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Item Id", 
                                               "field_path" : "shopping_cart,items,item_id",
                                               "sf_field" : ""}))
        #      Name
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Item Name", 
                                               "field_path" : "shopping_cart,items,name",
                                               "sf_field" : ""}))
        #      product code
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Product Code", 
                                               "field_path" : "shopping_cart,items,product_code",
                                               "sf_field" : ""}))
        #      Price
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Item Cost", 
                                               "field_path" : "shopping_cart,items,cost",
                                               "sf_field" : ""}))

        #      Price
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Total Line Item Cost", 
                                               "field_path" : "shopping_cart,items,total_cost",
                                               "sf_field" : ""}))
        #      Description
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Item Description", 
                                               "field_path" : "shopping_cart,items,description",
                                               "sf_field" : ""}))
     
        return fixedRows

registerATCT(GetPaidPFGSalesforceAdapter, PROJECTNAME)

try:
    from Products.Archetypes.interfaces import IMultiPageSchema
    classImplements(GetPaidPFGSalesforceAdapter, IMultiPageSchema)
except ImportError:
    pass

def handleOrderWorkflowTransition( order, event ):

    logger.info("handleOrderWorkflowTransition: %s, %s" % (order.finance_state, event.destination));

    # Only save the order if it has moved into the charged state
    # and the order was placed through PloneFormGen and the adapter is enabled
    if order.finance_state == event.destination and event.destination == workflow_states.order.finance.CHARGED:
        logger.info("Recording order");

        annotation = IAnnotations(order.shopping_cart)
        if "getpaid.SalesforcePloneFormGenAdapter.added" in annotation:
            getPaidFieldMap = annotation["getpaid.SalesforcePloneFormGenAdapter.GetPaidSFMapping"]

            salesforce = getToolByName(getSite(), 'portal_salesforcebaseconnector')
            sObject = [];
            
            # Loop over cart items creating an sObject for each
            index = 0;
            mappingCount = 0
            for item in order.shopping_cart.items():
                sObject.append(annotation["getpaid.SalesforcePloneFormGenAdapter.sObject"].copy())

                mappingCount = len(sObject[index].keys())
                for mapping in getPaidFieldMap:
                    if len(mapping['sf_field']) > 0:
                        value = _getValueFromOrder(order, item, mapping['field_path'])

                        if value is not None:
                            # Make sure we have found a value and that
                            # the form field wasn't left blank.  If it was we
                            # don't care about passing along that value, since
                            # the Salesforce object field may have it's own ideas
                            # about data types and or default values
                            sObject[index][mapping['sf_field']] = value
                            mappingCount += 1

                index += 1

            # mappingCount is a bit of a hack.  IT will calculate to the same
            # value for each item since the mapping is the same
            # I want to verify that I have a mapping other than type
            if mappingCount > 1:
                results = salesforce.create(sObject)
                for result in results:
                    if result['success']:
                        logger.debug("Successfully created new %s %s in Salesforce" % \
                                     (sObject[0]['type'], result['id']))
                    else:
                        logger.error('Failed to create new %s in Salesforce: %s' % \
                                     (sObject[0]['type'], result['errors'][0]['message']))
            else:
                logger.warn('No valid field mappings found. Not calling Salesforce.')
            
def _getValueFromOrder(order, item, fieldPath):
    split_field_path = fieldPath.split(',')
    
    # If items is in the split field path, then just call getattr on the item
    if "items" in split_field_path:
        # Item is actually a dict of item_id : item
        if split_field_path[-1] == "total_cost":
            # This is a hack since the line item object doesn't store total cost,
            # calculate it
            value = item[1].cost * item[1].quantity

        else:
            func = getattr(item[1], split_field_path[-1], None)
            if callable(func):
                value = func()
            else:
                value = func
    else:
        
        # Name is split since salesforce requires them to be
        if split_field_path[-1] == "first_name":
            fullName = order.contact_information.name
            value = fullName.split(' ', 1)[0]

        elif split_field_path[-1] == "last_name":
            fullName = order.contact_information.name
            names = fullName.split(' ', 1)

            # If the given name is a single word we'll end up using the same for
            # first and last.  I think that's better than crashing
            if len(names) == 2:
                value = names[1]
            else:
                value = names[0]

        # Salesforce only has 1 field for street address so we combine line 1 and 2
        elif split_field_path[-1] == "bill_address_street":
            line_1 = order.billing_address.bill_first_line
            line_2 = order.billing_address.bill_second_line

            value = "\n".join((line_1, line_2))
            
        elif split_field_path[-1] == "ship_address_street":
            line_1 = order.shipping_address.ship_first_line
            line_2 = order.shipping_address.ship_second_line

            value = "\n".join((line_1, line_2))
            
        # for all other elememts, call getattr starting with the order
        else:
            obj = order
            for attr in split_field_path:
                obj = getattr(obj, attr, None)
                if callable(obj):
                    value = obj()
                else:
                    value = obj

    return value
    
