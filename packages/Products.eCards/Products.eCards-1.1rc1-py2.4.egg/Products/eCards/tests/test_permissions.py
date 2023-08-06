# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.eCards.tests import base
from Products.eCards.config import SendECard

class TestProductPermissions(base.eCardTestCase):
    """ Ensure that our eCard product classes and objects
        fullfill their contractual interfaces
    """
    def afterSetUp(self):
        # all of our tests need an eCard object
        self.setupCollection()
        self.setupContainedECard()
        self.ecard = self.folder.collection.ecard
        
        # get our view
        self.view = self.ecard.restrictedTraverse('ecardpopup_browserview')
        
        self.membership = self.portal.portal_membership
    
    def testCustomECardPermissionConfigured(self):
        """We setup a permission for the sending of eCards that can easily 
           be overridden in cases where this is wanted as a priveleged feature.
        """
        self.failUnless('eCards: Send eCard' in [r['name'] for r in self.portal.permissionsOfRole('Manager') if r['selected']])
        self.failUnless('eCards: Send eCard' in [r['name'] for r in self.portal.permissionsOfRole('Anonymous') if r['selected']])
    
    def testAnonHasAccessToPopupView(self):
        """Our view is protected by the eCards.SendECard permission
           We ensure that anonymous can access that view by default
        """
        self.logout()
        self.failUnless(self.portal.portal_membership.isAnonymousUser())
        self.failUnless(self.membership.checkPermission(SendECard, self.ecard))
        
    def testViewProtectedUponRoleModification(self):
        """Our view is protected by the eCards.SendECard permission, which
           by default should be allowable by all.
           
           However we want people to be able make this "anonymous"
           protected activity.  The following test demonstrates that.
        """
        self.portal.manage_permission(SendECard, ('Manager',), acquire=0)
        self.failIf('eCards: Send eCard' in [r['name'] for r in self.portal.permissionsOfRole('Anonymous') if r['selected']])
        
        # test permissions as anon
        self.logout()
        self.failUnless(self.portal.portal_membership.isAnonymousUser())
        self.failIf(self.membership.checkPermission(SendECard, self.ecard))
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductPermissions))
    return suite
