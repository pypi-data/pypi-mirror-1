from cStringIO import StringIO
from zope.component import adapts
from zope.interface import implements

from xm.hitcounter.interfaces import IHitcounter,IHitcountable
from xm.hitcounter.core import _hit_manager
from xm.hitcounter import logger

from zope.i18n.negotiator import negotiator
from threading import Lock
lock = Lock()

known_browsers = """ABrowse
Acoo Browser
America Online Browser
AmigaVoyager
AOL
Arora
Avant Browser
Beonex
BonEcho
Camino
Cheshire
Chimera
CometBird
Crazy Browser
Cyberdog
Deepnet Explorer
Dillo
Elinks
Enigma Browser
Epiphany
Fennec
Firebird
Flock
Fluid
Galaxy
Galeon
GranParadiso
GreenBrowser
Hana
HotJava
IBM WebExplorer
IBrowse
iCab
Iceape
IceCat
Iceweasel
iNet Browser
Iron
K-Meleon
K-Ninja
Kapiko
Kazehakase
KKman
KMLite
Konqueror
Links
Lobo
lolifox
Lunascape
Lynx
Maxthon
Midori
Minefield
Minimo
MultiZilla
MyIE2
NCSA_Mosaic
NetFront
NetNewsWire
Netscape
NetSurf
OmniWeb
Orca
Oregano
Phoenix
QtWeb Internet Browser
retawq
Safari
SeaMonkey
Shiira
Shiretoko
Sleipnir
Stainless
Sunrise
TeaShark
w3m
WorldWideWeb"""

class HitcounterAdapter:
    """Adapter to count clicks for IOI"""
    
    implements(IHitcounter)
    adapts(IHitcountable)
    _count = 0
    
    def __init__(self, context):
        self.context = context

    def hitCount_new(self,request=None):
        """ count object view """
        _hit_manager.do_hit( self.context )
        
        
    def getHitCount_new(self):
        """get count for object view"""
        _hit_manager.get_hit( self.context )


    def hitCount(self,request=None, key=''):
        """ count object view """
        '''
        if request:
            if request['HTTP_REFERER'].startswith( self.context.absolute_url() ): 
                print "skipped  request['HTTP_REFERER']=", request['HTTP_REFERER']
                print "self.context.absolute_url()=", self.context.absolute_url()
                return  
        '''        
        if not request:
            request = self.context.request
        if not self.requestFromBrowser(request):
            return 0   
        if 0:  #do not use cookie for a moment
            if request:
                cookie_name = self.context.absolute_url()
                if request.has_key(cookie_name):
                    return
                request.response.setCookie(cookie_name, 1)
        if key:
            if 0: #block hits summapr for now
                lock.acquire()
                _hits = getattr ( self.context, '_hits_', {} )
                _hits[key] = _hits.get(key, 0) + 1
                self.context._hits = _hits # update zodb
                ret = _hits[key]
                lock.release()
            else:
                ret = 0
            self.logHit(request, key, ret)
        else:    
            lock.acquire()
            self.context._hit_count =  getattr ( self.context, '_hit_count', 0) + 1
            ret = self.context._hit_count
            lock.release()
            _hit_manager.add_hit(self.context) 
        return ret
        
    def hitCount_noindex(self,request=None):
        """ count object view """
        self.context._hit_count =  getattr ( self.context, '_hit_count', 0) + 1
        
    def getHitCount(self, key=''):
        """get count for object view"""
        if key:
            lock.acquire() 
            _hits = getattr ( self.context, '_hits_', {} )
            ret = _hits.get(key, 0) 
            lock.release()
        else:
            lock.acquire() 
            ret = getattr ( self.context, '_hit_count', 0)
            lock.release()
        return ret

    def get_lang(self, request):
        if not request: return ''
        lang = request.get( 'set_language', '')
        if not lang: 
            langs = ['en','nl']
            lang = negotiator.getLanguage(langs, request)
        return lang
       
    def logHit(self, request, key, hits):
        params = request.get('hit_params','')
        lang = self.get_lang(request)
        log_str = "%s <> %s <> %s <> %d <> %s" % (key, self.context.id, lang, hits, params)
        logger.debug(log_str)

    def requestFromBrowser(self, request):
        if hasattr( request, 'isBrowser'):
             return request['isBrowser']

        def _setBC(isBrowser):
             request.form['isBrowser'] = isBrowser
             return isBrowser

        user_agent = request['HTTP_USER_AGENT']
        #from http://www.useragentstring.com/pages/useragentstring.php

        #quick whitlist
        if user_agent.find(' MSIE ') > 0:
            #quick check for microsoft ie
            return _setBC(True)
        if user_agent.find(' Firefox/') > 0 and user_agent.find(' Gecko/') > 0:
            #quick check for mozilla firefox
            return _setBC(True)
        if user_agent.find(' Chrome/') > 0 and user_agent.find(' AppleWebKit/') > 0:
            #quick check for Chrome 
            return _setBC(True)
        if user_agent.find('Opera/') == 0 or user_agent.find(' Opera ') > 0:
            #quick check for Opera
            return _setBC(True)

        # quick blacklist
        if user_agent.find(' Googlebot') > 0 or user_agent.find(' Yahoo! Slurp') > 0 or user_agent.find('msnbot/') > 0:
            return _setBC(False)
        
        known_b = StringIO(known_browsers)            
        for line in known_b:
           line = ' '+line.rstrip()
           if user_agent.find(line) > 0:
               self.context.plone_log("hit-counting:"+line+" ua:"+user_agent)
               return _setBC(True)
        self.context.plone_log("NOT hit-counting:"+user_agent)
        return _setBC(False)

