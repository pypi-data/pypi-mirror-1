# Integration tests specific to our eCards product
#

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from base64 import decodestring
from Products.eCards.tests import base
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost

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

class TestCollectionBrowserViews(base.eCardTestCase):
    """ Ensure that our eCardCollection's browser
        view
    """
    def afterSetUp(self):
        self.workflow = self.portal.portal_workflow
        
        # all of our tests need a collection object
        self.setupCollection()
        
        # get our view
        self.view = self.folder.collection.restrictedTraverse('ecardcollection_browserview')
    
    def testCollectionGetECardsForView(self):
        # setup our contained
        self.setupContainedECard()
        
        # we have subitems at this point, but our view method 
        # returns a false value as none of the sub eCards have been published
        self.failUnless(len(self.folder.collection.objectIds()))
        self.failIf(self.view.getCardsForView())
        
        # become manager (doesn't really matter how or by who this happens) publish 
        # our eCard and we should now be getting results per the catalog search criteria
        self.setRoles(['Manager',])
        self.workflow.doActionFor(self.folder.collection.ecard, 'publish')
        self.failUnless(self.view.getCardsForView())
        
        # become normal test runner
        self.logout()
        self.login('test_user_1_')
    
    def testCollectionViewECardsDictReturnsNeededData(self):
        # setup our contained
        self.setupContainedECard()
        
        # become manager (doesn't really matter how or by who this happens) publish 
        # our eCard and we should now be getting results per the catalog search criteria
        self.setRoles(['Manager',])
        self.workflow.doActionFor(self.folder.collection.ecard, 'publish')
        
        # become normal test runner
        self.logout()
        self.login('test_user_1_')
        
        # get first element of first subarray
        cardDict = self.view.getCardsForView()[0][0]
        
        for key in ('title','description','thumbnail_html','url','width',):
            self.failUnless(cardDict.has_key(key),"Key %s does not exist \
                in our card dict" % key)
    
    def testGetECardsPerRowReturnsEmptyListWithNoECards(self):
        # we really just want an empty list at first
        # the default eCardsPerRow value is 5, thus the tests are based on that
        self.assertEqual(5, self.folder.collection.getECardsPerRow())
        self.failIf(self.view.getCardsForView())
    
    def testGetECardsForViewTwoDimensionalArray(self):
        # first some setup, create n-1 eCards in our collection
        numCards = 7
        self.massECardProducer(numCards)
        
        # this should be numCards - 1 per range(1,numCards), see base.py
        cardsInCollection = len(self.folder.collection.objectIds())
        self.assertEqual(numCards - 1, cardsInCollection)
        
        # the default eCardsPerRow value is 5, thus the tests are based on that
        self.assertEqual(5, self.folder.collection.getECardsPerRow())        
        # we should have a two dimensional array with the following attributes 
        # (written in pseudocode):
        
        #   1) len(viewReturnedECards) == (cardsInCollection / eCardsPerRow)
        self.assertEqual(len(self.view.getCardsForView()), \
            ((cardsInCollection / self.folder.collection.getECardsPerRow()) + self.determineRemainderOffset(cardsInCollection))) 
        
        #   2) len(viewReturnedECards[-1]) == cardsInCollection % eCardsPerRow
        # our final, possibly unfilled element should have the full number items in its row
        self.assertEqual(len(self.view.getCardsForView()[-1]), self.folder.collection.getECardsPerRow())
        # we should however, only have the remainder of num cards divided by cards per row of 
        # meaningful data (i.e. not '') in the last element
        self.assertEqual(len([eCardDict for eCardDict in self.view.getCardsForView()[-1] if eCardDict != '']), \
           cardsInCollection % self.folder.collection.getECardsPerRow() or self.folder.collection.getECardsPerRow())
        
        # now lets update the number of items per row and recalculate
        self.folder.collection.setECardsPerRow(3)
        # we want a 2-dimensional array w/ possible final, unfilled last row (ala [item,'','',])
        self.assertEqual(len(self.view.getCardsForView()), \
            ((cardsInCollection / self.folder.collection.getECardsPerRow()) + self.determineRemainderOffset(cardsInCollection))) 
        # our final, possibly unfilled element should have the full number items in its row
        self.assertEqual(len(self.view.getCardsForView()[-1]), self.folder.collection.getECardsPerRow())
        # we should however, only have the remainder of num cards divided by cards per row of 
        # meaningful data (i.e. not '') in the last element
        self.assertEqual(len([eCardDict for eCardDict in self.view.getCardsForView()[-1] if eCardDict != '']), \
            cardsInCollection % self.folder.collection.getECardsPerRow() or self.folder.collection.getECardsPerRow())
        
        # now lets update the number of items per row to the number of cards contained and recalculate
        self.folder.collection.setECardsPerRow(6)
        self.assertEqual(len(self.view.getCardsForView()), \
            ((cardsInCollection / self.folder.collection.getECardsPerRow()) + self.determineRemainderOffset(cardsInCollection))) 
        self.assertEqual(len(self.view.getCardsForView()[-1]), \
            cardsInCollection % self.folder.collection.getECardsPerRow() or self.folder.collection.getECardsPerRow()) # XXX FIX ME --> [item,,,]
    
    def testAppropriateThumbSchemaImageReturnedByView(self):
        # setup our contained
        self.setupContainedECard()
        
        # become manager (doesn't really matter how or by who this happens) publish 
        # our eCard and we should now be getting results per the catalog search criteria
        self.setRoles(['Manager',])
        self.workflow.doActionFor(self.folder.collection.ecard, 'publish')
        
        # upload to image, test the html
        self.folder.collection.ecard.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnless('image_thumb' in self.view.getCardsForView()[0][0]['thumbnail_html'])
        
        # upload to image, test the html
        self.folder.collection.ecard.setThumb(TEST_GIF, mimetype='image/gif', filename='testthumb.gif')
        self.failUnless('thumb_thumb' in self.view.getCardsForView()[0][0]['thumbnail_html'])
        
        # become normal test runner
        self.logout()
        self.login('test_user_1_')
    
    def testThumbSizeOverrideableOnCollectionLevel(self):
        # setup our contained
        self.setupContainedECard()

        # become manager (doesn't really matter how or by who this happens) to publish 
        # our eCard and we should now be getting results per the catalog search criteria
        self.setRoles(['Manager',])
        self.workflow.doActionFor(self.folder.collection.ecard, 'publish')

        # upload to image, test the html
        self.folder.collection.ecard.setImage(TEST_GIF, mimetype='image/gif', filename='test.gif')
        self.failUnless('image_thumb' in self.view.getCardsForView()[0][0]['thumbnail_html'])

        # now upload the thumb to ensure that our field namespace is correct
        self.folder.collection.ecard.setThumb(TEST_GIF, mimetype='image/gif', filename='testthumb.gif')
        self.failUnless('thumb_thumb' in self.view.getCardsForView()[0][0]['thumbnail_html'])
        
        # test thumb as mini
        self.folder.collection.setThumbSize('mini')
        self.failUnless('thumb_mini' in self.view.getCardsForView()[0][0]['thumbnail_html'])
        
        # test thumb as original
        self.folder.collection.setThumbSize('original')
        self.failUnless('thumb' in self.view.getCardsForView()[0][0]['thumbnail_html'])
    
    def testViewReturnsECardsWithinCollectionOnly(self):
        # setup our collection & contained
        self.setupContainedECard()
        
        # setup an alternate collection and ecard
        self.folder.invokeFactory('eCardCollection', 'mycollection')
        self.folder.mycollection.invokeFactory('eCard', 'myecard')
        
        # become manager (doesn't really matter how or by who this happens) publish 
        # our eCard and we should now be getting results per the catalog search criteria
        self.setRoles(['Manager',])
        self.workflow.doActionFor(self.folder.collection.ecard, 'publish')
        self.workflow.doActionFor(self.folder.mycollection.myecard, 'publish')
        
        # become normal test runner
        self.logout()
        self.login('test_user_1_')
        
        # make sure our view isn't returning ecards from all collections
        # we can't return more than exist
        self.failIf(len(self.folder.collection.objectIds()) < \
            len([eCardDict for eCardDict in self.view.getCardsForView()[0] if eCardDict != '']))
    
    def testViewReturnsECardsAsOrderedByPositionInParent(self):
        # setup several eCards
        for i in range(4):
            # create
            self.folder.collection.invokeFactory('eCard', 'ecard%s' % i)
            # workflow transition
            self.setRoles(['Manager',])
            self.workflow.doActionFor(self.folder.collection['ecard%s' % i], 'publish')
          
        # reorder, 2 moves to first, 1 moves to last
        self.folder.collection.moveObjectsByDelta(['ecard2'], -100)
        self.folder.collection.moveObjectsByDelta(['ecard1'], +100)
        
        for i in range(4):
            self.folder.collection['ecard%s' % i].reindexObject(idxs=['getObjPositionInParent',])
        
        # become normal test runner
        self.logout()
        self.login('test_user_1_')
        
        self.assertEqual([ecard_obj.absolute_url() for ecard_obj in self.folder.collection.objectValues()], 
                         [ecard['url'] for ecard in self.view.getCardsForView()[0] if ecard != ''])
        
        
        

class TestECardPopupBrowserViews(base.eCardTestCase):
    """ Ensure that our eCardCollection's browser
        view
    """
    def afterSetUp(self):
        
        # setup MailHostMock
        sm = self.portal.getSiteManager()
        sm.registerUtility(base.MailHostMock('MailHost'), IMailHost)
        self.mailhost = getToolByName(self.portal, 'MailHost')
        
        # all of our tests need an eCard object
        self.setupCollection()
        self.setupContainedECard()
        
        # get our view
        self.view = self.folder.collection.ecard.restrictedTraverse('ecardpopup_browserview')
    
    def testPopupViewSendsEmail(self):
        # mock form vars
        mail_to = 'jane@example.com'
        mail_from = 'john@example.com'
        
        options = {
            'subject': "Jane has sent you an eCard!",
            'friend_first_name': "Jane",
            'comment': "You'll love this picture!",
            'sender_first_name': "John",
            'credits': "Photo courtesy of Plone Foundation",
            # XXX change me
            'emailAppendedMessage': "Make a contribution at Plone.org",
            'image_url': "http://nohost/ecardimage",
        }
        
        # trigger the email
        self.view.sendECard(
            message = self.portal.portal_skins.ecards_templates.email_template(**options),
            full_to_address = mail_to,
            full_from_address = mail_from,
            subject = options['subject'],
        )
        
        # assert that a message was sent and it had some realistic data
        self.assertEqual(self.mailhost.n_mails, 1)
        self.assertEqual(self.mailhost.mto, mail_to)
        self.assertEqual(self.mailhost.mfrom, mail_from)
        decoded_mail_text = decodestring(self.mailhost.mail_text)
        for v in options.values():
            self.failUnless(v in decoded_mail_text, "The value %s was not found in the mail text")
    
    def testPopupViewStripNewLines(self):
        for s in ('Message', '\nMessage', '\rMessage', '\n\rMessage\n\r'):
            self.assertEqual('Message', self.view.stripNewLines(s))


if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCollectionBrowserViews))
    suite.addTest(makeSuite(TestECardPopupBrowserViews))
    return suite
    