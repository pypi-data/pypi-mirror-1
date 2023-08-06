from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from xm.hitcounter.core import _hit_manager

class MostPopularBase(object):

    limit = 10

    def search_by_hits(self):

        _hit_manager.add_hit(None) #update cache
        
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        query = {   'hit_countable':'True',
                    'sort_limit':10
                 }
        limit = self.limit
        q = catalog.makeAdvancedQuery(query)
        srt = [('hit_count', 'desc')]
        
        #results = context.queryCatalog(  REQUEST=query, sort_limit=limit)
        #print "len( results )=", len( results )
        #import pdb; pdb.set_trace()
        try:
            #pass
            results = catalog.evalAdvancedQuery(q, tuple(srt) ) [:limit]
        except:
            results = []
        #return results
        
        #for brain in results :print brain.getObject().id, brain.hit_count
        #print "-"*72 ; print
        return filter (lambda x: x.hit_count!="000000000000", results)

    