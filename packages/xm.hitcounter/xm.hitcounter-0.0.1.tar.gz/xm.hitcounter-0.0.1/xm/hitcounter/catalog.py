# zope imports
from zope.component.interfaces import ComponentLookupError

# CMFPlone imports
from Products.CMFPlone.CatalogTool import registerIndexableAttribute


from xm.hitcounter.interfaces import IHitcounter, IHitcountable


def hit_count(object, portal, **kwargs):
    try:
        ret = IHitcounter(object).getHitCount()
        return "%012d" % ret
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError


def hit_countable(object, portal, **kwargs):
    return str( IHitcountable.providedBy(object) )


registerIndexableAttribute('hit_count', hit_count)
registerIndexableAttribute('hit_countable', hit_countable)
