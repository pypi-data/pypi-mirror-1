# Register skin directory
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone import interfaces as plone_interfaces
from Products.CMFCore import permissions

from config import PROJECTNAME

import catalog
from content.container import HitcounterContainer

from Globals import INSTANCE_HOME
import os
HITLOG = os.environ['HITLOG']
if HITLOG:
    LOG_FILENAME = HITLOG+ "/stat.log"
else:
    LOG_FILENAME = INSTANCE_HOME + "/log/stat.log"
import logging
import logging.handlers
# Set up a specific logger with our desired output level
logger = logging.getLogger('mcb.stat')
logger.setLevel(logging.DEBUG)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=1)
handler.setFormatter( logging.Formatter("%(asctime)s <> %(message)s") )
logger.addHandler(handler)


def initialize(context):
    """initialize product (called by zope)"""
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    ADD_CONTENT_PERMISSION = permissions.AddPortalContent


    # Initialize portal tools
    tools = [HitcounterContainer]
    ToolInit( PROJECTNAME +' Tools',
                tools = tools,
                icon='tool.gif'
                ).initialize( context )

    # Initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom
