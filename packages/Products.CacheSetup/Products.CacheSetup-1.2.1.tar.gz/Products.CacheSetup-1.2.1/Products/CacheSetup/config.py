GLOBALS = globals()

PROJECT_NAME = 'CacheSetup'

PAGE_CACHE_MANAGER_ID = 'CacheSetup_PageCache'
OFS_CACHE_ID = 'CacheSetup_OFSCache'
RR_CACHE_ID = 'CacheSetup_ResourceRegistryCache'
CPM_ID = 'caching_policy_manager'

TOOL_ID = CACHE_TOOL_ID = 'portal_cache_settings'
TOOL_TITLE = 'Cache Configuration Tool'
CONFIGLET_ID = 'CacheSetupPrefs'

RULES_ID = 'rules'
BASERULE_TYPE = ('BaseCacheRule',)
RULE_TYPES = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')
HEADERSETS_ID = 'headersets'
HEADERSET_TYPES = ('HeaderSet',)
DEFAULT_POLICY_ID = 'with-caching-proxy'

TOOL_TYPE = 'CacheTool'
POLICY_TYPE = 'CachePolicy'
RULEFOLDER_TYPE = 'RuleFolder'
HEADERSETFOLDER_TYPE = 'HeaderSetFolder'
FOLDER_TYPES = (TOOL_TYPE, POLICY_TYPE, RULEFOLDER_TYPE, HEADERSETFOLDER_TYPE)
FOLDER_ITEM_TYPES = RULE_TYPES + HEADERSET_TYPES
TYPES = FOLDER_TYPES + FOLDER_ITEM_TYPES + BASERULE_TYPE


# TODO: remove this log() method
from zLOG import LOG, INFO, BLATHER
def log(msg, level=BLATHER):
    LOG(PROJECT_NAME, level, msg)


# A flag to support Plone 2.5.x 
from Products.CMFPlone.utils import getFSVersionTuple
_ploneVersion = getFSVersionTuple()
_major = _ploneVersion[0]
_minor = _ploneVersion[1]
if (_major == 2) and (_minor == 5):
    PLONE25 = True
else:
    PLONE25 = False


# Vocabulary for compression
USE_COMPRESSION = (
    ('never','Never'),
    ('always','Always'),
    ('accept-encoding','Use Accept-Encoding header'),
    ('accept-encoding+user-agent','Use Accept-Encoding and User-Agent headers'),
)
