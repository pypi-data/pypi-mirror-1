from getpaid.SalesforcePloneFormGenAdapter.config import PROJECTNAME
from getpaid.SalesforcePloneFormGenAdapter import HAS_PLONE25, HAS_PLONE30

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.utils import versionTupleFromString

from StringIO import StringIO

ALLTYPES = ('GetPaidPFGSalesforceAdapter',)
DEPENDENCIES = ('PloneFormGen',
                'DataGridField',
                'Products.salesforcepfgadapter')

def install(self):
    out = StringIO()
    
    print >> out, "Installing dependency products"
    portal_qi = getToolByName(self, 'portal_quickinstaller')
    for depend in DEPENDENCIES:
        if portal_qi.isProductInstallable(depend) and not portal_qi.isProductInstalled(depend):
            portal_qi.installProduct(depend)
    
    # We install our product by running a GS profile.  We use the old-style Install.py module 
    # so that our product works w/ the Quick Installer in Plone 2.5.x
    print >> out, "Installing GetPaidPFGSalesforceAdapter"
    setup_tool = getToolByName(self, 'portal_setup')
    if HAS_PLONE30:
        setup_tool.runAllImportStepsFromProfile(
                "profile-getpaid.SalesforcePloneFormGenAdapter:default",
                purge_old=False)
    else:
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-getpaid.SalesforcePloneFormGenAdapter:default')
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext(old_context)
    print >> out, "Installed types and added to portal_factory via portal_setup"
    
    
    # add the SalesforceGetPaidAdapter type as an addable type to FormField
    # This is not desirable to do with GS because we don't want to maintain a list of 
    # FormFolder's allowed_content_types and we don't want to overwrite existing settings
    print >> out, "Adding GetPaidPFGSalesforceAdapter to Form Field allowed_content_types"
    types_tool = getToolByName(self, 'portal_types')
    if 'FormFolder' in types_tool.objectIds():
        allowedTypes = types_tool.FormFolder.allowed_content_types
        
        if 'GetPaidPFGSalesforceAdapter' not in allowedTypes:
            allowedTypes = list(allowedTypes)
            allowedTypes.append('GetPaidPFGSalesforceAdapter')
            types_tool.FormFolder.allowed_content_types = allowedTypes
        
    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Add the field, fieldset, thanks and adapter types to types_not_searched
    # This is not desirable to do with GS because we don't want to maintain a list of 
    # the Portal's types_not_searched and we don't want to overwrite existing settings
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    for f in ALLTYPES:
        if f not in typesNotSearched:
            typesNotSearched.append(f)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Added form fields & adapters to types_not_searched"
    
    # Add the field, fieldset, thanks and adapter types to types excluded from navigation
    # This is not desirable to do with GS because we don't want to maintain a list of 
    # the Portal's metaTypesNotToList and we don't want to overwrite existing settings
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in ALLTYPES:
        if f not in typesNotListed:
            typesNotListed.append(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Added form fields & adapters to metaTypesNotToList"
    
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()


def uninstall(self):
    out = StringIO()
    
    portal_factory = getToolByName(self,'portal_factory')
    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')
    types_tool = getToolByName(self, 'portal_types')
    
    # remove salesforce adapter as a factory type
    factory_types = portal_factory.getFactoryTypes().keys()
    for t in ALLTYPES:
        if t in factory_types:
            factory_types.remove(t)
    portal_factory.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)
    print >> out, "Removed form adapters from portal_factory tool"
    
    # remove salesforce adapter from Form Folder's list of addable types
    if 'FormFolder' in types_tool.objectIds():
        allowedTypes = types_tool.FormFolder.allowed_content_types
        
        if 'GetPaidPFGSalesforceAdapter' in allowedTypes:
            allowedTypes = list(allowedTypes)
            allowedTypes.remove('GetPaidPFGSalesforceAdapter')
            types_tool.FormFolder.allowed_content_types = allowedTypes
            print >> out, "Removed GetPaidPFGSalesforceAdapter from FormFolder's allowedTypes"
    
    # remove our types from the portal's list of types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in ALLTYPES:
        if f in typesNotListed:
            typesNotListed.remove(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Removed form adapters from metaTypesNotToList"

    # remove our types from the portal's list of types_not_searched
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    for f in ALLTYPES:
        if f in typesNotSearched:
            typesNotSearched.remove(f)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Removed form adapters from types_not_searched"
    
    # Remove skin directory from skin selections
    skinstool = getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        if 'salesforce-getpaid-adapter_images' in path:
            path.remove('salesforce-getpaid-adapter_images')
            path = ','.join(path)
            skinstool.addSkinSelection(skinName, path)
    print >> out, "Removed salesforce-getpaid-adapter_images layer from all skin selections"
    
    print >> out, "\nSuccessfully uninstalled %s." % PROJECTNAME
    return out.getvalue()

