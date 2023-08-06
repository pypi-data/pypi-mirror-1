from Products.CMFCore.permissions import setDefaultRoles

## The Project Name
PROJECTNAME = "GetPaidPFGSalesforceAdapter"

## The skins dir
SKINS_DIR = 'skins'

## Globals variable
GLOBALS = globals()

## Permission for creating a SalesforcePFGAdapter
SFA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Salesforce GetPaid Adapter'
setDefaultRoles(SFA_ADD_CONTENT_PERMISSION, ('Manager','Owner',))

## Required field marker
REQUIRED_MARKER = "(required)"

SF_ADAPTER_TYPES = ['GetPaidPFGSalesforceAdapter',]
