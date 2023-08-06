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
import zope.component
from zope.interface import classImplements
from ZODB.POSException import ConflictError

# Plone imports
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

# PloneFormGen imports
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

# Local imports
from getpaid.SalesforcePloneFormGenAdapter.config import PROJECTNAME
from getpaid.SalesforcePloneFormGenAdapter import SalesforcePloneFormGenAdapterMessageFactory as _
from getpaid.SalesforcePloneFormGenAdapter import HAS_PLONE30

from Products.salesforcepfgadapter.content.salesforcepfgadapter import SalesforcePFGAdapter

# Get Paid events
from getpaid.core.interfaces import workflow_states, IShoppingCartUtility, IShippableOrder, IShippingRateService, IShippableLineItem
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
            label='Salesforce Object for Customer',
            description="""This object will hold the customer, address\
                 and potentially order items""",
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
    StringField('SFObjectTypeForItems',
        searchable=0,
        required=0,
        read_permission=ModifyPortalContent,
        default=u'',
        mutator='setSFObjectTypeForItems',
        widget=SelectionWidget(
            label='Salesforce Object for Items',
            description="""This object will hold the order items. It\
                  is optionally. If blank, the above object will\
                   be used, with a new SF record created for each item""",
            i18n_domain = "getpaidpfgsalesforceadapter",
            label_msgid = "label_salesforce_type_for_items_text",
            ),
        vocabulary='displaySFObjectTypesForItems',
        ),
    DataGridField('getPaidCustomerFieldMap',
         searchable=0,
         required=1,
         read_permission=ModifyPortalContent,
         schemata='field mapping',
         columns=('field_path', 'form_field', 'sf_field'),
         fixed_rows = "generateGetPaidCustomerFormFieldRows",
         allow_delete = False,
         allow_insert = False,
         allow_reorder = False,
         widget = DataGridWidget(
             label='Get Paid Customer fields to Salesforce fields mapping',
             label_msgid = "label_salesforce_getpaid_customer_field_map",
             description="""The following Form Fields are provided\
                 by the GetPaid customer & order. Choose the appropriate \
                 Salesforce Field for each Form Field.""",
             description_msgid = 'help_salesforce_getpaid_customer_field_map',
             columns= {
                 "field_path" : FixedColumn("Form Fields (path)", visible=False),
                 "form_field" : FixedColumn("GetPaid Customer Fields"),
                 "sf_field" : SelectColumn("Salesforce Fields", 
                                           vocabulary="buildSFFieldOptionList")
             },
             i18n_domain = "getpaidpfgsalesforceadapter",
             ),
         ),
    DataGridField('getPaidItemFieldMap',
         searchable=0,
         required=1,
         read_permission=ModifyPortalContent,
         schemata='field mapping',
         columns=('field_path', 'form_field', 'sf_field'),
         fixed_rows = "generateGetPaidItemFormFieldRows",
         allow_delete = False,
         allow_insert = False,
         allow_reorder = False,
         widget = DataGridWidget(
             label='Get Paid Item fields to Salesforce fields mapping',
             label_msgid = "label_salesforce_getpaid_item_field_map",
             description="""The following Form Fields are provided\
                 by the GetPaid order items. Choose the appropriate \
                 Salesforce Field for each Form Field.""",
             description_msgid = 'help_salesforce_getpaid_item_field_map',
             columns= {
                 "field_path" : FixedColumn("Form Fields (path)", visible=False),
                 "form_field" : FixedColumn("GetPaid Item Fields"),
                 "sf_field" : SelectColumn("Salesforce Fields", 
                                           vocabulary="buildSFFieldOptionListForItems")
             },
             i18n_domain = "getpaidpfgsalesforceadapter",
             ),
        ),
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
        self._fieldsForSFObjectForItemsType = {}

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

        # I need to figure out which cart to get.  The default, or a session
        # to do that I find the first getpaid adapter. I then look for the 
        # attr success_callback
        formFolder = aq_parent(self)
        adapters = formFolder.objectValues('GetpaidPFGAdapter')
        cart = None
        if (len(adapters) and adapters[0].success_callback == '_one_page_checkout_success'):
            cartKey = "multishot:%s" % formFolder.title
            cart = scu.get(self, key=cartKey)
        else:
            cart = scu.get(self, create=True)

        if (cart == None):
            logger.info("Unable to get cart")
        else:
            # Ideally I'd want to associate this with the item, but I have no 
            # guarentee that it has been created at this point.  It all depends
            # on the order the adapters run.
            annotation = IAnnotations(cart)

            if "getpaid.SalesforcePloneFormGenAdapter.adapters" in annotation:
                adapters = annotation["getpaid.SalesforcePloneFormGenAdapter.adapters"]

                if not self.title in adapters:
                    adapters.append(self.title)
            else:
                adapters = [self.title]

            annotation["getpaid.SalesforcePloneFormGenAdapter.adapters"] = adapters

            annotationKey = "getpaid.SalesforcePloneFormGenAdapter.%s" % self.title

            sObject = self._buildSObjectFromForm(fields, REQUEST)
            data = {}
            data['sObject'] = sObject
            data['sItemObject'] = dict(type=self.SFObjectTypeForItems)
            data['SFObjectForCustomer'] = self.SFObjectType
            data['SFObjectForItems'] = self.SFObjectTypeForItems

            data['GetPaidCustomerSFMapping'] = self.getPaidCustomerFieldMap
            data['GetPaidItemSFMapping'] = self.getPaidItemFieldMap
   
            annotation[annotationKey] = data

    security.declareProtected(ModifyPortalContent, 'buildSFFieldOptionListForItems')
    def buildSFFieldOptionListForItems(self):
        """Returns a DisplayList of all the fields
           for the currently selected Salesforce object
           type.
        """

        tmp = self._fieldsForSFObjectType
        if self._fieldsForSFObjectForItemsType != "":
            self._fieldsForSFObjectType = self._fieldsForSFObjectForItemsType

        ret = self.buildSFFieldOptionList()

        self._fieldsForSFObjectType = tmp

        return ret

    security.declareProtected(ModifyPortalContent, 'displaySFObjectTypesForItems')
    def displaySFObjectTypesForItems(self):
        logger.debug('Calling displaySFObjectTypesForItems()')        
        """ returns vocabulary for available Salesforce Object Types 
            we can create. 
        """
        types = self._querySFObjectTypes()
        typesDisplay = DisplayList()
        typesDisplay.add("", "")

        for type in types:
            typesDisplay.add(type, type)

        return typesDisplay
    

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
        _purgeInvalidMapping('getPaidCustomerFieldMap')

    security.declareProtected(ModifyPortalContent, 'setSFObjectTypeForItems')
    def setSFObjectTypeForItems(self, newType):
        """When we set the Salesforce object type,
           we also need to reset all the possible fields
           for our mapping selection menus.
        """
        logger.debug('Calling setSFObjectTypeForItems()')
        
        def _purgeInvalidMapping(fname):
            accessor = getattr(self, self.Schema().get(fname).accessor)
            mutator = getattr(self, self.Schema().get(fname).mutator)
            
            eligible_mappings = []
            for mapping in accessor():
                if mapping.has_key('sf_field') and not \
                        self._fieldsForSFObjectForItemsType.has_key(mapping['sf_field']):
                    continue
                
                eligible_mappings.append(mapping)
            
            mutator(tuple(eligible_mappings))

        # set the SFObjectType
        self.SFObjectTypeForItems = newType

        # This is a little hack.  My parent class uses a member variable in
        # _querySFFieldsForType so I trick.  Sneaky me...
        tmp = self.SFObjectType
        if self.SFObjectTypeForItems != "":
            self.SFObjectType = self.SFObjectTypeForItems
        
        # clear out the cached field info
        self._fieldsForSFObjectForItemsType = self._querySFFieldsForType()
        
        # undo my trickiery
        self.SFObjectType = tmp

        # purge mappings that are no longer valid
        _purgeInvalidMapping('getPaidItemFieldMap')        

    security.declareProtected(ModifyPortalContent, 'generateGetPaidCustomerFormFieldRows')
    def generateGetPaidCustomerFormFieldRows(self):
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
                                  initialData={"form_field" : "Billing Address Name", 
                                               "field_path" : "billing_address,bill_name",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Billing Address Organization", 
                                               "field_path" : "billing_address,bill_organization",
                                               "sf_field" : ""}))

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
                                  initialData={"form_field" : "Shipping Address Name", 
                                               "field_path" : "shipping_address,ship_name",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Address Organization", 
                                               "field_path" : "shipping_address,ship_organization",
                                               "sf_field" : ""}))

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
                                               "field_path" : "creation_date",
                                               "sf_field" : ""}))
        # Total Price
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Total", 
                                               "field_path" : "getTotalPrice",
                                               "sf_field" : ""}))

        # Transaction Id
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Transaction Id", 
                                               "field_path" : "user_payment_info_trans_id",
                                               "sf_field" : ""}))
        # Credit Card Last 4
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "CC Last 4", 
                                               "field_path" : "user_payment_info_last4",
                                               "sf_field" : ""}))

        # Shipping
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Service", 
                                               "field_path" : "shipping_service",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Method", 
                                               "field_path" : "shipping_method",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Weight", 
                                               "field_path" : "shipping_weight",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Shipping Cost", 
                                               "field_path" : "shipping_cost",
                                               "sf_field" : ""}))

        return fixedRows

    security.declareProtected(ModifyPortalContent, 'generateGetPaidItemFormFieldRows')
    def generateGetPaidItemFormFieldRows(self):
        """This method returns a list of rows for the field mapping
           ui. One row is returned for each field on the GetPaid order.
        """
        fixedRows = []


        if self.SFObjectTypeForItems != "" and self.SFObjectTypeForItems != self.SFObjectType:
            fixedRows.append(FixedRow(keyColumn="form_field",
                                      initialData={"form_field" : "Parent SF Object", 
                                                   "field_path" : "parent-sf-object",
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
        #      product sku
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Product SKU", 
                                               "field_path" : "shopping_cart,items,sku",
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

        #     Discount fields are deduced by looking at annotations
        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Discount Code", 
                                               "field_path" : "shopping_cart,items,discount_code",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Discount Title", 
                                               "field_path" : "shopping_cart,items,discount_title",
                                               "sf_field" : ""}))

        fixedRows.append(FixedRow(keyColumn="form_field",
                                  initialData={"form_field" : "Discount Total", 
                                               "field_path" : "shopping_cart,items,discount_total",
                                               "sf_field" : ""}))
     
        return fixedRows

registerATCT(GetPaidPFGSalesforceAdapter, PROJECTNAME)

try:
    from Products.Archetypes.interfaces import IMultiPageSchema
    classImplements(GetPaidPFGSalesforceAdapter, IMultiPageSchema)
except ImportError:
    pass

def handleOrderWorkflowTransition( order, event ):
    # Only save the order if it has moved into the charged state
    # and the order was placed through PloneFormGen and the adapter is enabled
    if order.finance_state == event.destination and event.destination == workflow_states.order.finance.CHARGED:
        annotation = IAnnotations(order.shopping_cart)
        if "getpaid.SalesforcePloneFormGenAdapter.adapters" in annotation:
            adapters = annotation['getpaid.SalesforcePloneFormGenAdapter.adapters']

            salesforce = getToolByName(getSite(), 'portal_salesforcebaseconnector')
            for a in adapters:
                annotationKey = "getpaid.SalesforcePloneFormGenAdapter.%s" % a
                data = annotation[annotationKey]

                try:
                    executeAdapter(order, data, salesforce)
                except ConflictError:
                    raise
                except Exception, e:
                    # I catch everything since any uncaught exception here
                    # will prevent the order from moving to charged
                    logger.error("Exception saving order %s to salesforce: %s" % (order.order_id, e))
                    logger.info('Data: %s' % data)
                except:
                    logger.error("Unknown Exception saving order %s to salesforce" % (order.order_id))
                    logger.info('Data: %s' % data)


def executeAdapter(order, data, salesforce):
    sfObject = data['SFObjectForCustomer']
    sfObjectForItems = data['SFObjectForItems']
    getPaidCustomerFieldMap = data['GetPaidCustomerSFMapping']
    getPaidItemFieldMap = data['GetPaidItemSFMapping']

    if sfObjectForItems == "" or sfObjectForItems == sfObject:
        # Loop over the items mapping customer and item to same 
        # SFObject I will have multiple SF Objects
        sObject = [];
                
        # Loop over cart items creating an sObject for each
        for item in order.shopping_cart.items():
            obj = data['sObject'].copy()
            sObject.append(obj)

            _mapObject(order, item, obj, getPaidCustomerFieldMap)
            _mapObject(order, item, obj, getPaidItemFieldMap)

        results = salesforce.create(sObject)
        for result in results:
            if result['success']:
                logger.info("Successfully created new %s %s for order %s in Salesforce" % \
                                 (sObject[0]['type'], result['id'], order.order_id))
            else:
                for error in result['errors']:
                    logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                     (sObject[0]['type'], order.order_id, error['message']))
    else:
        # Loop over the items mapping customer and item to same SFObject
        # I will have multiple SF Objects

        # first create the customer obejct in SF
        obj = data['sObject'].copy()

        # I kind of think it's a hack to pass None for the item
        # the method expects it, but in this case will not use
        # it since I'm passing the customer field map.
        _mapObject(order, None, obj, getPaidCustomerFieldMap)

        results = salesforce.create(obj)
        if results[0]['success']:
            logger.info("Successfully created new %s %s for order %s in Salesforce" % \
                             (obj['type'], results[0]['id'], order.order_id))

            obj['id'] = results[0]['id']

            # Loop over cart items creating an sObject for each
            sObjects = []
            for item in order.shopping_cart.items():
                itemObj = data['sItemObject'].copy()
                sObjects.append(itemObj)

                _mapObject(order, item, itemObj, getPaidItemFieldMap, obj['id'])

            results = salesforce.create(sObjects)
            for result in results:
                if result['success']:
                    logger.info("Successfully created new %s %s in Salesforce" % \
                                     (sObjects[0]['type'], result['id']))
                else:
                    for error in result['errors']:
                        logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                         (sObjects[0]['type'], order.order_id, error['message']))

        else:
            for error in results[0]['errors']:
                logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                 (obj['type'], order.order_id, error['message']))

def _mapObject(order, item, sfObject, fieldMap, parentSFField=None):
    # Copy address into a dummy object so I can handle ship same as billing
    # it would be nice if the field names in the shipping and billing
    # structures where the same

    for mapping in fieldMap:
        if len(mapping['sf_field']) > 0:

            if mapping['field_path'] == "parent-sf-object":
                value = parentSFField
            else:
                value = _getValueFromOrder(order, item, mapping['field_path'])
                            
            if value is not None:
                # Make sure we have found a value and that
                # the form field wasn't left blank.  If it was we
                # don't care about passing along that value, since
                # the Salesforce object field may have it's own ideas
                # about data types and or default values
                sfObject[mapping['sf_field']] = value

def _getValueFromOrder(order, item, fieldPath):
    split_field_path = fieldPath.split(',')
    
    # If items is in the split field path, then just call getattr on the item
    if "items" in split_field_path:
        # Item is actually a dict of item_id : item
        if split_field_path[-1] == "total_cost":
            # This is a hack since the line item object doesn't store total cost,
            # calculate it
            value = item[1].cost * item[1].quantity

        elif split_field_path[-1] == "discount_code":
            value = ""
            annotation = IAnnotations(item[1])
            if "getpaid.discount.code" in annotation:
                value = annotation["getpaid.discount.code"]

        elif split_field_path[-1] == "discount_title":
            value = ""
            annotation = IAnnotations(item[1])
            if "getpaid.discount.code.title" in annotation:
                value = annotation["getpaid.discount.code.title"]

        elif split_field_path[-1] == "discount_amount":
            value = ""
            annotation = IAnnotations(item[1])
            if "getpaid.discount.code.discount" in annotation:
                value = annotation["getpaid.discount.code.discount"]
            
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

            if line_2 is None:
                value = line_1
            else:
                value = "\n".join((line_1, line_2))
            
        elif split_field_path[-1] == "ship_address_street":
            if order.shipping_address.ship_same_billing:
                line_1 = order.billing_address.bill_first_line
                line_2 = order.billing_address.bill_second_line
            else:
                line_1 = order.shipping_address.ship_first_line
                line_2 = order.shipping_address.ship_second_line

            if line_2 is None:
                value = line_1
            else:
                value = "\n".join((line_1, line_2))

        elif split_field_path[-1] == "ship_city":
            if order.shipping_address.ship_same_billing:
                value = order.billing_address.bill_city
            else:
                value = order.shipping_address.ship_city

        elif split_field_path[-1] == "ship_state":
            if order.shipping_address.ship_same_billing:
                value = order.billing_address.bill_state
            else:
                value = order.shipping_address.ship_state

        elif split_field_path[-1] == "ship_country":
            if order.shipping_address.ship_same_billing:
                value = order.billing_address.bill_country
            else:
                value = order.shipping_address.ship_country

        elif split_field_path[-1] == "ship_postal_code":
            if order.shipping_address.ship_same_billing:
                value = order.billing_address.bill_postal_code
            else:
                value = order.shipping_address.ship_postal_code

        elif split_field_path[-1] == "shipping_service":
            value = getShippingService(order)

        elif split_field_path[-1] == "shipping_method":
            value = getShippingMethod(order)

        elif split_field_path[-1] == "shipping_weight":
            value = getShipmentWeight(order)

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
    
def getShippingService(order):
    if not hasattr(order,"shipping_service"):
        return None
    infos = order.shipping_service
    if infos:
        return infos

def getShippingMethod(order):
    # check the traversable wrrapper
    if not IShippableOrder.providedBy( order ):
        return None
    
    service = zope.component.queryUtility( IShippingRateService,
                                           order.shipping_service )
    
    # play nice if the a shipping method is removed from the store
    if not service: 
        return None
        
    return service.getMethodName( order.shipping_method )
    
def getShipmentWeight(order):
    """
    Lets return the weight in lbs for the moment
    """
    # check the traversable wrrapper
    if not IShippableOrder.providedBy( order ):
        return None

    totalShipmentWeight = 0
    for eachProduct in order.shopping_cart.values():
        if IShippableLineItem.providedBy( eachProduct ):
            weightValue = eachProduct.weight * eachProduct.quantity
            totalShipmentWeight += weightValue
    return totalShipmentWeight
