# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.eCards.tests import base
from Products.CMFCore.utils import getToolByName
from Products.eCards.config import ALLTYPES, ALLSKINS

class TestProductUnInstallation(base.eCardTestCase):
    """ Ensure that our product plays nicely and uninstalls correctly.
    """
    def afterSetUp(self):
        self.types      = self.portal.portal_types
        self.properties = self.portal.portal_properties
        self.factory    = self.portal.portal_factory
        self.qi         = self.portal.portal_quickinstaller
        self.workflow   = self.portal.portal_workflow
        self.skins      = self.portal.portal_skins
        self.css        = self.portal.portal_css
        
        self.eCardTypes  = ALLTYPES
        self.eCardSkins  = ALLSKINS
        
        # uninstall our product
        if self.qi.isProductInstalled('eCards'):
            self.qi.uninstallProducts(products=['eCards',])
    
    def testQIDeemsProductUninstalled(self):
        """Make sure the product is uninstalled in the eyes of the portal_quickinstaller"""
        self.failIf(self.qi.isProductInstalled('eCards'))

    def testAdapterTypeNotRegisteredOnUninstall(self):
        for t in self.eCardTypes:
            self.failIf(t in self.types.objectIds(),
                "Type %s is still registered with the types tool after uninstallation." % t)

    def testFactoryTypesRemovedOnUninstall(self):
        for t in self.eCardTypes:
            self.failIf(t in self.factory.getFactoryTypes(),
                "Type %s is still a factory type after uninstallation." % t)

    def testTypesNotSearchedRemovedOnUninstall(self):
        # XXX - revisit me
        pass

    def testTypesNotListedRemovedOnUninstall(self):
        metaTypesNotToList  = self.properties.navtree_properties.getProperty('metaTypesNotToList')
        for t in self.eCardTypes:
            self.failIf(t in metaTypesNotToList,
                "Type %s is still in the list of metaTypesNotToList after uninstallation" % t)
    
    def testSkinsRemovedOnUninstall(self):
        """Our all important skin layer(s) should be registered with the site."""
        for prodSkin in self.eCardSkins:
            self.failIf(prodSkin in self.skins.objectIds(),
                "The skin %s is still registered with the skins tool after uninstallation" % prodSkin)
    
    def testSkinLayersRemovedOnUninstall(self):
        """We need our product's skin directories to show up below custom as one of the called
           upon layers of our skin's properties
        """
        for selection, layers in self.skins.getSkinPaths():
            for specific_layer in self.eCardSkins:
                self.failIf(specific_layer in layers, "The %s layer \
                    still appears in the layers of Plone's %s skin after uninstall" % (specific_layer,selection))
    
    def testWorkflowToolNoLongerMaintainsWorkflowChainForRemovedType(self):
        for t in self.eCardTypes:
            self.failIf(self.workflow._chains_by_type.has_key(t), "The %s type \
                still appears to have a workflow chain with the workflow tool" % t)
    
    def testECardsNoLongerInTypesUsingViewInListing(self):
        """Make sure the eCard type shows up in the list of types needing view action in listings
        """
        # make sure we haven't lost the defaults
        self.failUnless('Image' in self.properties.site_properties.typesUseViewActionInListings)
        # and that our type appears in the list
        self.failIf('eCard' in self.properties.site_properties.typesUseViewActionInListings)
    
    def testResourceRegistriesNoLongerManagingECardResources(self):
        """We ensure that our css is no longer lying around upon uninstallation.
        """
        self.failIf('ecards.css' in self.css.getResourceIds())
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductUnInstallation))
    return suite
