# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.eCards.tests import base
from Products.CMFCore.utils import getToolByName

from Products.eCards.interfaces import IECardCollection, IECard, \
    IECardCollectionView, IECardPopupView
from zope.interface.verify import verifyObject, verifyClass

from Products.eCards.content.ecard import eCard
from Products.eCards.content.ecardcollection import eCardCollection
from Products.eCards.browser import eCardCollectionView, eCardPopupView

class TestProductInterfaces(base.eCardTestCase):
    """ Ensure that our eCard product classes and objects
        fullfill their contractual interfaces
    """
    def afterSetUp(self):
        pass
    
    def testContentInterfaces(self):
        """ Some basic boiler plate testing of Interfaces and objects"""
        # verify IECardCollection
        self.failUnless(IECardCollection.implementedBy(eCardCollection))
        self.failUnless(verifyClass(IECardCollection, eCardCollection))
        
        # verify IECard
        self.failUnless(IECard.implementedBy(eCard))
        self.failUnless(verifyClass(IECard, eCard))
    
    def testObjectInstances(self):
        # setup our content objects
        self.setupContainedECard()
        
        # verify we're an object of the expected class
        self.failUnless(isinstance(self.folder.collection, eCardCollection))
        self.failUnless(isinstance(self.folder.collection.ecard, eCard))
        
    def testContentObjectsVerify(self):
        # setup our content objects
        self.setupContainedECard()
        
        self.failUnless(verifyObject(IECardCollection, self.folder.collection))
        self.failUnless(verifyObject(IECard, self.folder.collection.ecard))
    
    def testBrowserViewInterfaces(self):
        # verify IECardCollectionView
        self.failUnless(IECardCollectionView.implementedBy(eCardCollectionView))
        self.failUnless(verifyClass(IECardCollectionView, eCardCollectionView))
        
        # verify IECardPopupView
        self.failUnless(IECardPopupView.implementedBy(eCardPopupView))
        self.failUnless(verifyClass(IECardPopupView, eCardPopupView))
    
    def testBrowserViewsVerify(self):
        # just need a collection here
        self.setupCollection()
        self.setupContainedECard()
        
        # get our views
        collection_view = self.folder.collection.restrictedTraverse('ecardcollection_browserview')
        popup_view      = self.folder.collection.ecard.restrictedTraverse('ecardpopup_browserview')
        
        # verify we're an object of the expected class
        self.failUnless(isinstance(collection_view, eCardCollectionView))
        self.failUnless(verifyObject(IECardCollectionView, collection_view))
        
        self.failUnless(isinstance(popup_view, eCardPopupView))
        self.failUnless(verifyObject(IECardPopupView, popup_view))
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInterfaces))
    return suite
        