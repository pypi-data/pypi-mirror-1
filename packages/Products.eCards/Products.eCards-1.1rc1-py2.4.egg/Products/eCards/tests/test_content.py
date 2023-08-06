# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.eCards.tests import base
from Products.CMFCore.utils import getToolByName

from Globals import package_home
PACKAGE_HOME = package_home(globals())

def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data

TEST_GIF = loadImage('test.gif')


class TestContentEditing(base.eCardTestCase):
    """ Ensure that our eCard product installs and 
        correctly configures our portal.
    """
    def afterSetUp(self):
        self.properties = self.portal.portal_properties
        self.types      = self.portal.portal_types
    
    def testECardCollectionAddable(self):
        self.folder.invokeFactory('eCardCollection', 'collection')
        self.failUnless('collection' in self.folder.objectIds())
    
    def testSetGetOnECardCollection(self):
        # add the collection
        self.folder.invokeFactory('eCardCollection', 'collection')
        
        # set all fields
        # XXX -- finish me!!
        self.folder.collection.setTitle('My eCard Collection')
        self.folder.collection.setDescription('My description')
        self.folder.collection.setText('<p>Some Body text</p>')
        self.folder.collection.setEmailSubject('Your friend sent you an eCard')
        self.folder.collection.setEmailAppendedMessage('<p>Some more information about the organization that made this eCard possible</p>')
        self.folder.collection.setECardsPerRow(5)
        self.folder.collection.setThumbSize('tile')
        
        # test the field values
        self.assertEqual(self.folder.collection.Title(), 'My eCard Collection')
        self.assertEqual(self.folder.collection.Description(), 'My description')
        self.assertEqual(self.folder.collection.getText(), '<p>Some Body text</p>')
        self.assertEqual(self.folder.collection.getEmailSubject(), 'Your friend sent you an eCard')
        self.assertEqual(self.folder.collection.getEmailAppendedMessage(), '<p>Some more information about the organization that made this eCard possible</p>')
        self.assertEqual(self.folder.collection.getECardsPerRow(),5)
        self.assertEqual(self.folder.collection.getThumbSize(),'tile')
    
    def testECardCollectionCardsPerRowIntegerOnly(self):
        """Because code in our eCardCollectionView browser based
           view depends on receiving an integer for mathematical 
           operations, we make sure in our test that this doesn't change.
        """
        self.folder.invokeFactory('eCardCollection', 'collection')
        self.assertRaises(ValueError,self.folder.collection.setECardsPerRow,'Some String')
    
    def testECardCollectionSchemata(self):
        """Make sure that we have our needed schemata for configuration of 
           email settings.
        """
        # add the collection
        self.folder.invokeFactory('eCardCollection', 'collection')
        self.failUnless('email' in self.folder.collection.Schema().getSchemataNames())
    
    def testECardAddableToCollection(self):
        self.folder.invokeFactory('eCardCollection', 'collection')
        self.folder.collection.invokeFactory('eCard', 'ecard')
        self.failUnless('ecard' in self.folder.collection.objectIds())
    
    def testECardNotGloballyAddable(self):
        self.assertRaises(ValueError, self.folder.invokeFactory, 'eCard', 'ecard')
    
    def testSetGetOnECard(self):
        """Make sure we can add the actual eCard successfully"""
        # add the collection and contained eCard
        self.folder.invokeFactory('eCardCollection', 'collection')
        self.folder.collection.invokeFactory('eCard', 'ecard')
        
        # set all fields
        # XXX -- finish me!!
        self.folder.collection.ecard.setCredits('Some great photographer')
        self.folder.collection.ecard.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.folder.collection.ecard.setThumb(TEST_GIF, mimetype='image/gif', filename='test.gif')
        
        # test the field values
        self.assertEqual(self.folder.collection.ecard.getCredits(), 'Some great photographer')
        self.failUnlessEqual(self.folder.collection.ecard.getImage().data, TEST_GIF)
        self.failUnlessEqual(self.folder.collection.ecard.getThumb().data, TEST_GIF)
    
    def testThumbTagOnECard(self):
        # add the collection and contained eCard
        self.setupContainedECard()
        self.folder.collection.ecard.setThumb(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnless('128' in self.folder.collection.ecard.thumbtag(scale='thumb'))
        self.failUnless('thumb_thumb' in self.folder.collection.ecard.thumbtag(scale='thumb'))
    
    def testCollectionEmailAppendedMessageDefaultsToCorrectFormat(self):
        """Ensure that the default format for our eCard Collection's
           HTML-rich email body is actually HTML.
        """
        self.setupCollection()
        self.assertEqual('text/html', self.folder.collection.Schema().get('emailAppendedMessage').default_content_type)
    
    def testCollectionCanBeOrderedInParent(self):
        """See: http://plone.org/products/ecards/issues/10
           Thanks Weblion: https://weblion.psu.edu/trac/weblion/changeset/2608
        """
        # setup several collections
        self.folder.invokeFactory('eCardCollection', 'collection1')
        self.folder.invokeFactory('eCardCollection', 'collection2')
        self.folder.invokeFactory('eCardCollection', 'collection3')
        
        # prove that we can reorder
        self.folder.moveObjectsByDelta(['collection3'], -100)
        self.failUnless(self.folder.getObjectPosition('collection3') == 0,
            "eCardCollection subobject 'collection3' should be at position 0.")
        
        

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentEditing))
    return suite
