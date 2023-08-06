# zope imports
from zope.interface import implements

# iqpp imports
from xm.hitcounter.interfaces import IPopularityCounter
from persistent.dict import PersistentDict
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder,BaseFolderSchema 
from xm.hitcounter.popularity_counter import PopularityCounter
from AccessControl import ClassSecurityInfo

schema=BaseFolderSchema 

from Products.CMFCore.utils import UniqueObject

class HitcounterContainer(UniqueObject, BaseFolder, PopularityCounter):
    """Hitcounter container"""
    
    implements(IPopularityCounter)
    security = ClassSecurityInfo()
    meta_type   = 'xm.hitcounter'
    
   


atapi.registerType(HitcounterContainer, 'xm.hitcounter')
