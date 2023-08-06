"""
CacheSetup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import Schema

from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField

from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import MultiSelectionWidget

from Products.CacheSetup.utils import base_hasattr
from Products.CacheSetup.config import PROJECT_NAME
import base_cache_rule as BaseCacheRule

schema = BaseContent.schema.copy() + Schema((

    TextField(
        'description',
        required=0,
        allowable_content_types = ('text/plain',),
        default='A cache rule for objects associated with an PolicyHTTPCachingManager',
        write_permission = permissions.ManagePortal,
        widget=TextAreaWidget(
            label='Description',
            cols=60,
            rows=5,
            description='Basic documentation for this cache rule')),

    StringField(
        'cacheManager',
        default='HTTPCache',
        vocabulary='getPolicyHTTPCacheManagerVocabulary',
        enforce_vocabulary=1,
        write_permission = permissions.ManagePortal,
        widget=SelectionWidget(
            label='Cache Manager',
            description='This rule will apply to content associated with the specified PolicyHTTPCacheManager manager.')),

    LinesField(
        'types',
        default=(),
        multiValued = 1,
        vocabulary='getContentTypesVocabulary',
        enforce_vocabulary = 1,
        write_permission = permissions.ManagePortal,
        widget=MultiSelectionWidget(
            label='Types',
            size=10,
            description='Please select the types to which this rule applies.  Leave empty for all types.')),

    LinesField(
        'ids',
        default=(),
        multiValued = 1,
        write_permission = permissions.ManagePortal,
        widget=LinesWidget(
            label='Ids',
            size=5,
            description='IDs of the objects to which this rule applies.  Leave empty for all objects.')),

    LinesField(
        'cacheStop',
        default=('portal_status_message','statusmessages'),
        write_permission = permissions.ManagePortal,
        widget=LinesWidget(
            label='Cache Preventing Request Items',
            description='Tokens in the request that prevent caching if present')),

    )) + BaseCacheRule.header_set_schema
                       
schema['id'].widget.ignore_visible_ids=True                       
schema['id'].widget.description="Should not contain spaces, underscores or mixed case. An 'X-Caching-Rule-Id' header with this id will be added."

class PolicyHTTPCacheManagerCacheRule(BaseCacheRule.BaseCacheRule):
    """
    """
    security = ClassSecurityInfo()
    archetype_name = 'PolicyHTTPCacheManager Cache Rule'
    portal_type = meta_type = 'PolicyHTTPCacheManagerCacheRule'
    __implements__ = BaseCacheRule.BaseCacheRule.__implements__
    schema = schema
    _at_rename_after_creation = True

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

    def getContentTypesVocabulary(self):
        tt = getToolByName(self, 'portal_types')
        types_list = [(t.getId(), t.getProperty('title') and t.getProperty('title') or t.getId()) for t in tt.listTypeInfo()]
        types_list.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(tuple(types_list))
    
    def getPolicyHTTPCacheManagerVocabulary(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        phcm = portal.objectIds(spec='Policy HTTP Cache Manager')
        return DisplayList(tuple([(p,p) for p in phcm]))

    def getEtag(self, request, object, view, member, header_set=None):
        pass

    security.declarePublic('getHeaderSet')
    def getHeaderSet(self, request, object, view, member):
        # see if this rule applies
        if not base_hasattr(object, 'ZCacheable_getManagerId'):
            return
        if object.ZCacheable_getManagerId() != self.getCacheManager():
            return
        types = self.getTypes()
        if not base_hasattr(object, 'meta_type'):
            return
        if types and object.meta_type not in types:
            return
        if not base_hasattr(object, 'getId'):
            return
        ids = self.getIds()
        if ids and object.getId() not in ids:
            return

        header_set = self._getHeaderSet(request, object, view, member)
        return header_set

registerType(PolicyHTTPCacheManagerCacheRule, PROJECT_NAME)

__all__ = (
    'PolicyHTTPCacheManagerCacheRule',
)
