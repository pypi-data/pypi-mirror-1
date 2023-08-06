"""Rule folder implementation

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions

from Products.Archetypes.atapi import OrderedBaseFolder
from Products.Archetypes.atapi import registerType

from Products.CacheSetup.interfaces import ICacheToolFolder
from Products.CacheSetup.config import PROJECT_NAME
from nocatalog import NoCatalog


class RuleFolder(NoCatalog, OrderedBaseFolder):
    """A container for rule objects"""

    __implements__ = (OrderedBaseFolder.__implements__, ICacheToolFolder)
    
    security = ClassSecurityInfo()
    archetype_name = 'Rule Folder'
    portal_type = meta_type = 'RuleFolder'
    global_allow = 0
    allowed_content_types = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')

    actions = (
        {'action':      'string:$object_url',
         'category':    'object',
         'id':          'view',
         'name':        'Cache Setup',
         'permissions': (permissions.ManagePortal,),
         'visible':     False},
    )

    aliases = {
        '(Default)':    'cache_policy_item_config',
        'view' :        'cache_policy_item_config',
        'edit' :        'cache_policy_item_config'
    }

registerType(RuleFolder, PROJECT_NAME)
