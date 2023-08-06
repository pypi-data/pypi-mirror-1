import os.path
__version__ = open(os.path.join(__path__[0],'VERSION.txt')).read().strip()

from AccessControl import allow_module

from Products.Archetypes import public as atapi
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory

from content import *
from content.cache_tool import CacheTool
from content.caching_policy_manager import CSCachingPolicyManager
from permissions import initialize as initialize_permissions
import config

registerDirectory('skins', config.GLOBALS)

def initialize(context):
    """Product Initialization
    """
    import patch, patch_cmf, patch_five
    patch.run()
    patch_cmf.run()
    patch_five.run()

    tools = (CacheTool, CSCachingPolicyManager)

    try:
        cmfutils.ToolInit(
        config.PROJECT_NAME + ' Tool',
        tools = tools,
        icon = 'cachesetup_tool_icon.gif',
        ).initialize(context)
    except TypeError:
        cmfutils.ToolInit(
        config.PROJECT_NAME + ' Tool',
        tools = tools,
        product_name = config.PROJECT_NAME,
        icon = 'cachesetup_tool_icon.gif',
        ).initialize(context)

    allow_module('Products.CacheSetup.config')

    # Ask Archetypes to handback all the type information needed
    # to make the CMF happy.
    types = atapi.listTypes(config.PROJECT_NAME)
    content_types, constructors, ftis = \
        atapi.process_types(types, config.PROJECT_NAME)
    permissions = initialize_permissions()

    # We want to register each each type with its own permission,
    # this will afford us greater control during system
    # configuration/deployment (and is a good recipe)
    # The pattern used here will create many item options in ZMI
    # menus, but is the only way that allows for things to still be
    # selectable in the UI. If they all had the same name, only the
    # first would be found.
    permissions = initialize_permissions()
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        cmfutils.ContentInit(
            atype.meta_type,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)
    
