from zope.interface import implements
from interfaces import IPopularityCounter
from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOBTree
import random
from threading import Lock
lock = Lock()

_dict = {}

class PopularityCounter(Persistent):
    implements(IPopularityCounter)
   
    def getStorage(self, keyword):
        stor = _dict.get( keyword,  getattr(self, keyword, {} )  )
        #print stor.__class__
        if stor.__class__ !=  _dict.__class__:
            z = {}
            z.update( stor.items() )
            stor = z
            
        if not stor: 
            setattr (self, keyword, stor)
            #_dict[keyword] = stor
        return stor
    
    def addItem(self, keyword, *args):
        """ add new location """
        lock.acquire()
        storage = self.getStorage(keyword)
        loc_id = "|".join(args)
        storage[ loc_id ] = storage.get( loc_id, 0 ) + 1
        setattr(self, keyword, storage)
        lock.release()
        
    def getMostPopular(self, keyword, count, shullfe=0):
        """ return count of most poular locations"""
        storage = self.getStorage(keyword)
        ls = storage .items()
        ls.sort( lambda x,y: cmp(y[1], x[1]) )
        ret = []
        if not ls: return ret
        max_ = ls[0][1]
        min_ = ls[-1][1]
        mid = (1.0*(max_+min_))/2
        ls = ls[:count]
        random.seed(25)
        random.shuffle(ls)
        for k,v in ls:
            font_sz = int( (90 * v)/mid ) + 40
            ret.append( (k.split('|'),v, font_sz ) )
        return ret
        