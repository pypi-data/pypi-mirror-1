# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.eCards.tests import base
from Products.CMFCore.utils import getToolByName
from Products.eCards.config import ALLTYPES, ALLSKINS

class TestProductInstallation(base.eCardTestCase):
    """ Ensure that our eCard product installs and 
        correctly configures our portal.
    """
    def afterSetUp(self):
        self.properties = self.portal.portal_properties
        self.factory    = self.portal.portal_factory
        self.types      = self.portal.portal_types
        self.skins      = self.portal.portal_skins
        self.workflow   = self.portal.portal_workflow
        self.css        = self.portal.portal_css
        
        self.eCardTypes  = ALLTYPES
        self.eCardSkins  = ALLSKINS
    
    def testCoreProductsInstalled(self):
        CORE_PRODUCTS = ['eCards',]
        
        for prod in CORE_PRODUCTS:
            self.failUnless(self.portal.portal_quickinstaller.isProductInstalled(prod),
                "Core product %s is not already installed" % prod)
    
    def testPortalFactorySetup(self):
        for t in self.eCardTypes:
            self.failUnless(t in self.factory.getFactoryTypes(),
                "Type %s is not a factory types" % t)
    
    def testStockListedTypesNotPurged(self):
        metaTypesNotToList  = self.properties.navtree_properties.getProperty('metaTypesNotToList')
        self.failUnless(len(metaTypesNotToList) > len(self.eCardTypes))
    
    def testTypesNotListed(self):
        metaTypesNotToList  = self.properties.navtree_properties.getProperty('metaTypesNotToList')
        for t in self.eCardTypes:
            self.failUnless(t in metaTypesNotToList,
                "Type %s will show up in the nav and shouldn't" % t)
    
    def testCorePloneLayersStillPresent(self):
        """As was known to happen with legacy versions of GS working with the skins tool,
           it was easy to inadvertently remove need layers for the selected skin.  Here 
           we make sure this hasn't happened.
        """
        core_layers = ('plone_templates','plone_content',)
        
        for selection, layers in self.skins.getSkinPaths():
            for specific_layer in core_layers:
                self.failUnless(specific_layer in layers, "The %s layer \
                    does not appear in the layers of Plone's available skins" % specific_layer)
    
    def testECardTypesFTI(self):
        """We keep the eCardFTIMapping up to date as a
           static list of what the very important FTI settings
           are for our subclassed ATCT types and make sure they
           match the settings in the ZMI's portal_types tool.
        """
        eCardFTIMapping = [
            {"eCard":{
                    "title":"eCard",
                    "content_meta_type":"eCard",
                    "product":"eCards",
                    "global_allow":False,
                    "filter_content_types":False,
                    "content_icon":'ecard_icon.gif',
                    "factory":'addeCard',
                },},
            
            {"eCardCollection":{
                    "title":"eCard Collection",
                    "content_meta_type":"ECardCollection",
                    "product":"eCards",
                    "global_allow":True,
                    "filter_content_types":True,
                    "allowed_content_types":('eCard',),
                    "content_icon":'ecardcollection_icon.gif',
                    "factory":'addeCardCollection',
                },},
            
        ]
        
        for fti_type in eCardFTIMapping:
            for k,v in fti_type.items():
                type_obj = getattr(self.types,k)
                for type_attr, type_attr_value in v.items():
                    self.assertEquals(eval("type_obj.%s" % type_attr), type_attr_value,
                        "For type %s, the FTI value should be %s for the %s field \
                        types tool, but it's %s" % (k, type_attr_value, type_attr, eval("type_obj.%s" % type_attr)))
    
    def testBrowseToObjectViaViewAlias(self):
        """Test to prove fix to bug where upon adding an eCard to a collection
           one was taken directly to the index_html method, which on an image
           is the image within the web browser, which thereby takes the content
           edit away from the Plone UI, which is very baffling.
        """
        ecard_fti = self.types.eCard
        self.failUnless("/view" in \
            ecard_fti.getActionObject('object/view').getActionExpression())
    
    def testFSDVInSkinsTool(self):
        """Test the the needed file system directory views have
           been registered with the skins tool.
        """
        for prodSkin in self.eCardSkins:
            self.failUnless(prodSkin in self.skins.objectIds(),
                "The skin %s was not registered with the skins tool" % prodSkin)
    
    def testFSDVContainSkinResourcesTemplates(self):
        """This is a bit of overkill, but since eCards is being targetted
           past pre-customerize Plone releases, we want various aspects to be
           customizable via the ZMI.  We make sure those items, roughly, exist
           in their appropriate skin layers. This also provides some coverage
           of a missing registerDirectory call w/in __init__ for the package.
        """
        self.failUnless('ecardcollection_icon.gif' in self.skins.ecards_images.objectIds())
        self.failUnless('ecardcollection_view' in self.skins.ecards_templates.objectIds())
        self.failUnless('ecards.css' in self.skins.ecards_styles.objectIds())
    
    def testSkinShowsUpInToolsLayers(self):
        """We need our product's skin directories to show up below custom as one of the called
           upon layers of our skin's properties
        """
        for selection, layers in self.skins.getSkinPaths():
            for specific_layer in self.eCardSkins:
                self.failUnless(specific_layer in layers, "The %s layer \
                    does not appear in the layers of Plone's %s skin" % (specific_layer,selection))
    
    def testCorePloneLayersStillPresent(self):
        """As was known to happen with legacy versions of GS working with the skins tool,
           it was easy to inadvertently remove need layers for the selected skin.  Here 
           we make sure this hasn't happened.
        """
        core_layers = ('plone_styles','plone_templates',)
        
        for selection, layers in self.skins.getSkinPaths():
            for specific_layer in core_layers:
                self.failUnless(specific_layer in layers, "The %s layer \
                    does not appear in the layers of Plone's available skins" % specific_layer)
    
    def testChainsForECardTypes(self):
        """Make sure that the workflow chains for our
           eCard types are resonable and reflect the expected
           Plone defaults
        """
        self.assertEqual('plone_workflow',self.workflow.getChainForPortalType('eCard')[0])
        self.assertEqual('folder_workflow',self.workflow.getChainForPortalType('eCardCollection')[0])
    
    def testECardsInTypesUsingViewInListing(self):
        """Make sure the eCard type shows up in the list of types needing view action in listings
        """
        # make sure we haven't lost the defaults
        self.failUnless('Image' in self.properties.site_properties.typesUseViewActionInListings)
        # and that our type appears in the list
        self.failUnless('eCard' in self.properties.site_properties.typesUseViewActionInListings)
    
    def testResourceRegistriesManagingCSSResources(self):
        """We register a css stylesheet on installation.  
           Here we ensure correct setup.
        """
        self.failUnless('ecards.css' in self.css.getResourceIds())
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstallation))
    return suite
