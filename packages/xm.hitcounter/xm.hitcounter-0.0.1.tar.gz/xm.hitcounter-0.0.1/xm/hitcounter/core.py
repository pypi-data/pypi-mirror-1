#hit counter core
import time
from threading import Lock

from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot

class CHitManager:
    "centralized hit manager"
    _hit_time =[]
    _hit_oid =[]
    _hit_traverse =[]
    cache_max = 60 # seconds
    lock = Lock()
    _str_root = ''
    
    def __init__(self):
        pass
        
    def get_root(self):
        return getUtility(ISiteRoot)
        
    def get_object_traverse_path(self, ob):
        ids = [ ]
        self._str_root = self._str_root or str( self.get_root() )
        while str(ob) != self._str_root:
            ids.insert(0, ob.id)
            ob = ob.aq_parent
        return ids
        
    def traverse_object(self, pth):
        ob = self.get_root()
        for id in pth: 
            ob = getattr(ob, id, None)
            if ob is None: break
        return ob    
    
    
    def add_hit(self, obj):
        """add to cache of objects waiting to be reindexed"""        
        now = time.time()
        c_pth = None
        
        self.lock.acquire() #lock search so object can't be reindexed twice
        
        if obj:
            pth = self.get_object_traverse_path(obj) 
            oid = "|".join(pth)
            if not oid in self._hit_oid: #check if new obj is in list
                #new obj - add it to lists
                self._hit_oid.append( oid ) #oid to find 
                self._hit_traverse.append(pth) #path to restore obj
                self._hit_time.append(now + self.cache_max ) #timeout for reindex
        if self._hit_time: #we have something cached
            if self._hit_time[0] < now: #check latest added if it's timed out
                c_pth = self._hit_traverse[0] #get path to traverse
                del self._hit_traverse[0]
                del self._hit_oid[0]
                del self._hit_time[0]
        self.lock.release()
        
        if not c_pth: return
        
        c_object = self.traverse_object(c_pth)
        if c_object: #we should have unique object here, other threads are supposed to add new entry for such obj
            c_object.reindexObject( ['hit_count'] )
        
    def get_hit(self, obj):
        return getattr ( obj, '_hit_count', 0)
    
_hit_manager = CHitManager()