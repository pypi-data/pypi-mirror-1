from zope.interface import Interface

class IECard(Interface):
    """eCard interface
    """
    def thumbtag():
        """Generate image tag using the api of the ImageField
        """
    

class IECardCollection(Interface):
    """eCard Collection interface
    """
    

class IECardCollectionView(Interface):
    """eCard Collection browser view
    """
    def getCardsForView():
        """Return a two dimensional array of images representing
           the number of images intended per row.
        """
    

class IECardPopupView(Interface):
    """eCard Collection browser view
    """
    def stripNewLines(str):
        """This method strips out linefeeds from
           any string in an effort to clamp down
           on potential spam sending vulnerabilities.
        """
    
    def sendECard():
        """Calls send on the MailHost object, protected
           by our custom Send eCard permission
        """
    

    