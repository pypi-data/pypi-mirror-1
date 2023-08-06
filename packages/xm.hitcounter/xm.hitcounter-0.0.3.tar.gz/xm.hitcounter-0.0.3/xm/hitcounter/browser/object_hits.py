# zope imports
from zope.interface import Interface
from zope.interface import implements
from Acquisition import aq_inner

# Five imports
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


# CMFCore imports
from Products.CMFCore.utils import getToolByName

# xm.hitcounter imports
from xm.hitcounter.interfaces import IHitcounter, IHitcountable


class IObjectHitsView(Interface):
    """
    """
    def countHit(self):
        """ """
  
    def getHits():
        """Returns hits for context.
        """

class ObjectHitsView(BrowserView):
    """
    """
    implements(IObjectHitsView)

    template = ViewPageTemplateFile('object_hits.pt')

    def getHits(self):
        """
        """
        hc = IHitcounter(self.context)
        return hc.getHitCount()

    def countHit(self):
        """
        """
        hc = IHitcounter(self.context)
        hc.hitCount()


class ObjectHitsViewlet(ViewletBase):
    """
    """
    implements(IObjectHitsView)

    render = ViewPageTemplateFile('object_hits.pt')

    def getHits(self):
        """
        """
        hc = IHitcounter(self.context)
        return hc.getHitCount()

from StringIO import StringIO
from PIL import Image, ImageDraw, ImageFont
import os.path
from Globals import package_home

g_font = 0

def get_font(sz):
    global g_font
    if g_font: return g_font
    #import pdb; pdb.set_trace()
    ph = package_home( globals())
    fontfile = os.path.join( ph, 'lsansd.ttf' )
    g_font = ImageFont.truetype(fontfile, sz)
    return g_font


def image_from_text(txt):
    #calc image size 1st
    img_sz = Image.new('RGBA', (20,18), (0,0,0,0))
    dr_sz = ImageDraw.Draw(img_sz)
    fnt = get_font(12)
    sz = dr_sz.textsize(txt, font=fnt)
    del dr_sz; del img_sz
    width = sz[0]+20
    
    img = Image.new('RGBA', (width,18), (0,0,0,0))
    dr = ImageDraw.Draw(img)
    
    dr.text((10,3),txt,fill="#5B5237", font=fnt)

    new_file = StringIO()
    img.save(new_file, 'PNG')
    new_file.seek(0)
    return new_file.read()

class ObjectHitsImage(object):
    "here comes 1px transparent gif"
    image_transp = '\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B'
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, **kw):
        """ do render """        
        key = self.request.get('key','')
        small = self.request.get('small', key) #keyed are small by default
        #force small: url?small=1   #force normal  url?small=&key=search
        
        context = aq_inner(self.context)
        hits = " "
        show = self.request.get('show', None )
        
        if IHitcountable.providedBy(context): #count hit for object 
            if show:  hits = IHitcounter(context).getHitCount(key)   
            else: hits = IHitcounter(context).hitCount(self.request,key)
        
        self.request.response.setHeader('content-type', 'image/png')
        self.request.response.setHeader('Cache-Control', 'no-cache')

        if small: 
            return self.image_transp
        else:                
            return image_from_text(str(hits))
        
    def getHits(self):
        """
        """
        hc = IHitcounter(self.context)
        return hc.getHitCount()        

