import logging
logger = logging.getLogger('xm.hitcounter: setuphandlers')
from config import PROJECTNAME
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from config import TOOL_NAME
##/code-section HEA

def setupHideToolsFromNavigation(context):
    """hide tools"""
    # uncatalog tools
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'hitcounter': # avoid infinite recursions
        return
    site = context.getSite()
    toolnames = [TOOL_NAME]
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)


def importVarious(context):
    """Import various settings.
    """
    # Set default permissions
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'hitcounter': # avoid infinite recursions
        return
    portal = context.getSite()
    setupHideToolsFromNavigation(context)
    #portal.manage_permission("xm.ranking: view",    ('Manager', 'Member', 'Anonymous'), 1)
    #portal.manage_permission('xm.ranking: rank',    ("Manager", "Member", "Anonymous"), 1)
    #portal.manage_permission('xm.ranking: details', ("Manager", "Member", "Anonymous"), 1)
    #portal.manage_permission("xm.ranking: manage",  ('Manager',), 1)
