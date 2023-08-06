from Products.eCards.config import PROJECTNAME, ALLTYPES, ALLSKINS, SendECard
from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def uninstall(self):
    out = StringIO()
    
    portal_factory = getToolByName(self,'portal_factory')
    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')
    types_tool = getToolByName(self, 'portal_types')

    # remove eCards as a factory types
    factory_types = portal_factory.getFactoryTypes().keys()
    for t in ALLTYPES:
        if t in factory_types:
            factory_types.remove(t)
    portal_factory.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)
    print >> out, "Removed eCards types from portal_factory tool"
    
    # remove our types from the portal's list of types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in ALLTYPES:
        if f in typesNotListed:
            typesNotListed.remove(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Removed eCards types from metaTypesNotToList"
    
    # remove our types from the portal's list of types using view in action listings
    typesUseViewAction = list(siteProperties.getProperty('typesUseViewActionInListings'))
    for f in ('eCard',):
        if f in typesUseViewAction:
            typesUseViewAction.remove(f)
    siteProperties.manage_changeProperties(typesUseViewActionInListings = typesUseViewAction)
    print >> out, "Removed eCard from typesUseViewActionInListings"
    
    # Remove skin directory from skin selections
    skinstool = getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        for specific_layer in ALLSKINS:
            if specific_layer in path:
                path.remove(specific_layer)
        path = ','.join(path)
        skinstool.addSkinSelection(skinName, path)
    
    print >> out, "Removed skin layers from all skin selections"
    
    # clean-up mapped workflow chains for GS configured types
    workflow_tool = getToolByName(self, 'portal_workflow')
    del workflow_tool._chains_by_type['eCardCollection']
    print >> out, "Removed the associated eCardCollection type chains"
    
    print >> out, "\nSuccessfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
    