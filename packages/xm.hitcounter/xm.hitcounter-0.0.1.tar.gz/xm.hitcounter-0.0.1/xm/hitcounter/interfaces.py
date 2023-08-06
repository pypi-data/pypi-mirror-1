# zope imports
from zope.interface import Interface, Attribute
from zope import schema
from config import _


class IHitcounterContainer(Interface):
    """Hitcounter Container"""

    title = schema.TextLine(title=_(u"Title"),
         description=_(u"The title of the hitcounter container"),
         required=False,
         default=u'',
    )

class IHitcountable(Interface):
    """Interface to be adapted to IHitcounter
    """

class IHitcounter(Interface):
    """Hit counter interface"""
         
    def hitCount(self, request=None, key=''):
        """ count object view"""
    
    def getHitCount(self, key=''):
        """get count for object view"""

    _count = Attribute("hit count")    

class IPopularityCounter(Interface):
    """ List of popular locations as user searches by location """
    
    def getStorage(self, keyword):
        """ return dict for keyword or create one"""
    
    def addItem(self, keyword, **kw):
        """ add new popualr item by keyword"""
        
    def getMostPopular(self, keyword, count):
        """ return count of most poular items by keyword"""