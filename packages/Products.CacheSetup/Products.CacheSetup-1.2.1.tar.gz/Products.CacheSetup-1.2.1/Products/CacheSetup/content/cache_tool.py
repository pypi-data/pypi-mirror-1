"""
CacheSetup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

$Id: $
"""

__authors__ = 'Geoff Davis <geoff@geoffdavis.net>'
__docformat__ = 'restructuredtext'

import sets
import urlparse

import zope.component
from zope.interface import implements

from Acquisition import aq_get
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import rolesForPermissionOn
from BTrees import Length
from DateTime import DateTime
from ZODB.POSException import ConflictError
from Products.Transience import Transience

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.utils import _checkPermission

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import OrderedBaseFolder
from Products.Archetypes.atapi import registerType

from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import LinesField

from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import StringWidget

from Products.Archetypes.debug import log_exc
from Products.CMFPlone import PloneMessageFactory as _

from Products.statusmessages.interfaces import IStatusMessage

from Products.CacheSetup.interfaces import ICacheTool
from Products.CacheSetup.interfaces import IPurgeUrls
from Products.CacheSetup.enabler import enableCacheFu
from Products.CacheSetup import config
from Products.CacheSetup import __version__
from nocatalog import NoCatalog

schema = BaseSchema.copy() + Schema((

    BooleanField(
        'enabled',
        default=False,
        write_permission = permissions.ManagePortal,
        widget=BooleanWidget(
            label='Enable CacheFu',
            description='Uncheck to turn off CacheFu\'s caching behavior.  Note: Disabling CacheFu '
                        'does not purge proxy or browser caches so stale content may still continue '
                        'to be served out of those caches.')),

    StringField(
        'activePolicyId',
        default=config.DEFAULT_POLICY_ID,
        vocabulary='getActivePolicyVocabulary',
        write_permission = permissions.ManagePortal,
        widget=SelectionWidget(
            label='Active Cache Policy',
            description='Please indicate which cache policy to use.',
            condition='python:len(object.getActivePolicyVocabulary()) > 1')),

    # XXX: The cacheConfig field is no longer used, and kept here hidden only so that we can migrate away from it
    StringField(  
        'cacheConfig',
        widget=SelectionWidget(
            label='Cache Configuration',
            visible={'edit': 'invisible', 'view': 'invisible'})), 

    StringField(
        'proxyPurgeConfig',
        required=1,
        default='no-purge',
        write_permission = permissions.ManagePortal,
        vocabulary=DisplayList((
            ('no-purge','No Purge (zope-only, or zope-behind-apache)'),
            ('no-rewrite','Simple Purge (squid/varnish in front)'),
            ('vhm-rewrite','Purge with VHM URLs (squid/varnish behind apache, VHM virtual hosting)'),
            ('custom-rewrite','Purge with custom URLs (squid/varnish behind apache, custom virtual hosting)'))),
        widget=SelectionWidget(
            label='Proxy Cache Purge Configuration',
            description='If you are using a caching proxy such as Squid or Varnish in front '
                        'of Zope, CacheFu needs to be able to tell this proxy to purge its '
                        'cache of certain pages. If Apache is in front of Squid/Varnish, then '
                        'this depends on Apache\'s "virtual hosting" configuration. The most common '
                        'Apache configuration generates VirtualHostMonster-style URLs with '
                        'RewriteRules/ProxyPass. If you have a legacy CacheFu 1.0 Squid-Apache '
                        'install or other custom Apache configuration, you may want to choose '
                        'the "custom URLs" option and customize the rewritePurgeUrls.py script.')),

    LinesField(
        'domains',
        edit_accessor='getDomains',
        write_permission = permissions.ManagePortal,
        widget=LinesWidget(
            label='Site Domains',
            description='Enter a list of domains for your site.  This is not needed if you chose "No Purge" '
                        'under the Proxy Cache Purge Configuration option above. '
                        'If your site handles both http://www.mysite.com:80 and http://mysite.com:80, '
                        'be sure to include both. Also include https versions of your domains if you use them. '
                        'Be sure to include a port for each site.')),

    LinesField(
        'squidURLs',
        edit_accessor='getSquidURLs',
        write_permission = permissions.ManagePortal,
        widget=LinesWidget(
            label='Proxy Cache Domains',
            description='Enter a list of domains for any purgeable proxy caches. This is not needed if '
                        'you chose "No Purge" or "Simple Purge" under "Proxy Cache Purge Configuration" '
                        'above. For example, if you are using Squid with Apache in front, there will '
                        'commonly be a single squid instance at http://127.0.0.1:3128')),

    StringField(
        'gzip',
        default='accept-encoding',
        write_permission = permissions.ManagePortal,
        vocabulary=DisplayList((
            ('never','Never'),
            ('always','Always'),
            ('accept-encoding','Use Accept-Encoding header'),
            ('accept-encoding+user-agent','Use Accept-Encoding and User-Agent headers'))),
        widget=SelectionWidget(
            label='Compression',
            description='Should Zope compress pages before serving them, and if so, what criteria '
                        'should be used to determine whether pages should be gzipped? The most common '
                        'settings are "Never" (no compression) or "Use Accept-Encoding header" '
                        '(only compress content if the browser explicitly declared support for compression).')),

    StringField(
        'varyHeader',
        default='Accept-Encoding',
        write_permission = permissions.ManagePortal,
        widget=StringWidget(
            label='Vary Header',
            size=60,
            description='Value for the Vary header.  If you are using gzipping, you may need to include '
                        '"Accept-Encoding" and possibly "User-Agent". If you are running a multi-lingual site, '
                        'you may also need "Accept-Language". Values should be separated by commas. '
                        '(Upon submit, this value will be cleaned up and checked for any obvious omissions)')),
    ))

schema['title'].default = config.TOOL_TITLE
schema['title'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}
schema['id'].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

class CacheTool(NoCatalog, OrderedBaseFolder, UniqueObject):
    """
    """

    implements(ICacheTool)
    archetype_name = 'Cache Configuration Tool'
    portal_type = meta_type = 'CacheTool'
    plone_tool = 1
    security = ClassSecurityInfo()
    schema = schema
    content_icon = 'cachesetup_tool_icon.gif'
    global_allow = 0
    allowed_content_types=('CachePolicy',)
    _catalog_count = None
    _permission_count = None
    _change_date = None

    actions = (
        {'action':      'string:$object_url',
         'category':    'object',
         'id':          'view',
         'name':        'Cache Setup',
         'permissions': (permissions.ManagePortal,),
         'visible':     False
        },
    )

    aliases = {
        '(Default)':    'cache_tool_config',
        'view' :        'cache_tool_config',
        'edit' :        'base_edit'
    }

    def __init__(self, oid, **kwargs):
        # keep track of the installed version
        OrderedBaseFolder.__init__(self, oid, **kwargs)
        self.installedversion = __version__

    def updateInstalledVersion(self):
        # call this method after a reinstall
        # to update installedversion tracking
        self.installedversion = __version__

    def initializeArchetype(self, **kwargs):
        # get values from other places before archetypes initializes them
        squid_urls = self._getSquidUrls()
        OrderedBaseFolder.initializeArchetype(self, **kwargs)
        # don't stomp on squid urls
        self._setSquidUrls(squid_urls)

    def getActivePolicyVocabulary(self, display=None):
        active = self.getActivePolicyId()
        vocabulary = [(p.getId(), p.Title()) for p in self.objectValues() if p.portal_type=="CachePolicy"]
        if display:
            vocabulary = [('(active policy)', '(active policy)')] + vocabulary
        return DisplayList(tuple(vocabulary))

    # if active is gone, find another
    def getActivePolicyId(self):
        policy_id = self.getField('activePolicyId').get(self)
        if getattr(self, str(policy_id), None) is None:
            rules = getattr(self, config.RULES_ID, None)
            if rules is not None:
                # we haven't migrated yet
                return ''
            else:
                # policy deleted so try the first one
                policies = self.objectValues()
                if len(policies):
                    policy_id = policies[0].getId()
                else:
                    # no policies so add a blank set
                    self.addPolicyFolder(config.DEFAULT_POLICY_ID, 'Default Cache Policy')
                    policy_id = config.DEFAULT_POLICY_ID
            self.setActivePolicyId(policy_id)
        return policy_id

    # use browser cookies to store current display policy id
    def setDisplayPolicy(self, id=None, camefrom=None, redirect=True):
        request = self.REQUEST
        response = request.response
        cookie_name = 'cachetool_policy'
        id = str(id)
        display_policy = getattr(self, id, None)
        if getattr(self, id, None) is None:
            # clear the cookie
            response.setCookie(cookie_name, '', path='/')
            id = None
        else:
            # expire cookie after 6 hours
            expires = (DateTime() + .25).toZone('GMT').rfc822()
            response.setCookie(cookie_name, id, path='/', expires=expires)
        if redirect:
            if camefrom is None:
                response.redirect('%s/cache_policy_config' % self.absolute_url())
            else:
                policy = self.getPolicy(id)
                response.redirect('%s/%s' % (policy.absolute_url(), camefrom))
        return ''

    def getEnabled(self):
        """Let's disable CacheFu if the file system version doesn't
        match the installed version to make sure we don't kill the site
        if the schemas have changed.
        """
        if getattr(self, 'installedversion', None) != __version__ :
            return False
        return self.getField('enabled').get(self)

    def setEnabled(self, value):
        # convert to boolean for backwards compat with Plone 2.5
        if not value or value == '0' or value == 'False':
            value = False
        else:
            value = True
        # if version mismatch, send status message
        if value and getattr(self, 'installedversion', None) != __version__ :
            IStatusMessage(self.REQUEST).addStatusMessage(
                    _(u"Refusing to enable CacheSetup until installed version matches "
                      u"filesystem version. Update/reinstall CacheSetup to fix."),
                    type="error")
        # change field only if different
        elif value != self.getField('enabled').get(self):
            self.getField('enabled').set(self, value)
            enableCacheFu(self, value)

    def getPolicy(self, policy_id=None):
        if policy_id is None:
            policy_id = self.getActivePolicyId()
        policy = getattr(self, policy_id, None)
        if policy is None:
            rules = getattr(self, config.RULES_ID, None)
            if rules is not None:
                # we haven't migrated yet
                policy = self
            else:
                # policy deleted so try the first one
                policies = self.objectValues()
                if len(policies):
                    policy = policies[0]
                else:
                    # no policies so add a blank set
                    self.addPolicyFolder(config.DEFAULT_POLICY_ID, 'Default Cache Policy')
                    policy = getattr(self, config.DEFAULT_POLICY_ID)
        return policy

    def getDisplayPolicy(self):
        request = self.REQUEST
        response = request.response
        cookie_name = 'cachetool_policy'
        id = request.cookies.get(cookie_name, '')
        display_policy = getattr(self, id, None)
        if display_policy is None:
            if id != '': response.setCookie(cookie_name, '', path='/')
            display_policy = self.getPolicy()
        return display_policy

    def getRules(self, policy_id=None):
        policy = self.getPolicy(policy_id)
        rules = getattr(policy, config.RULES_ID, None)
        if rules is None:
            policy_id = policy.getId()
            self.addRulesFolder(policy_id)
            rules = self.getRules(policy_id)
        return rules

    def getHeaderSets(self, policy_id=None):
        policy = self.getPolicy(policy_id)
        header_sets = getattr(policy, config.HEADERSETS_ID, None)
        if header_sets is None:
            policy_id = policy.getId()
            self.addHeaderSetsFolder(policy_id)
            header_sets = self.getHeaderSets(policy_id)
        return header_sets

    def getHeaderSetById(self, id):
        return getattr(self.getHeaderSets(), id)

    def addPolicyFolder(self, policy_id, policy_title, empty=None):
        policy = getattr(self, policy_id, None)
        if policy is not None:
            self.manage_delObjects(policy_id)
        self.invokeFactory(id=policy_id, type_name='CachePolicy')
        policy = getattr(self, policy_id)
        policy.unmarkCreationFlag()
        policy.setTitle(policy_title)
        policy.reindexObject()
        if empty is not None:
            policy_id = policy.getId()
            self.addRulesFolder(policy_id)
            self.addHeaderSetsFolder(policy_id)

    def addRulesFolder(self, policy_id):
        policy = getattr(self, policy_id)
        policy.allowed_content_types = ('RuleFolder',)
        policy.invokeFactory(id=config.RULES_ID, type_name='RuleFolder')
        policy.allowed_content_types = ()
        rules = self.getRules(policy.getId())
        rules.unmarkCreationFlag()
        rules.setTitle('Rules')
        rules.reindexObject()

    def addHeaderSetsFolder(self, policy_id):
        policy = getattr(self, policy_id)
        policy.allowed_content_types = ('HeaderSetFolder',)
        policy.invokeFactory(id=config.HEADERSETS_ID, type_name='HeaderSetFolder')
        policy.allowed_content_types = ()
        header_sets = self.getHeaderSets(policy.getId())
        header_sets.unmarkCreationFlag()
        header_sets.setTitle('Headers')
        header_sets.reindexObject()

    # ##### Counters for use in ETag/cache key building #####

    def updateChangeDate(self):
        # change_date is a DateTime that we will update 
        # every time we increment a counter
        if self._change_date is None:
            self._change_date = Transience.Increaser(DateTime())
        self._change_date.set(DateTime())

    def getChangeDate(self):
        return self._change_date()

    def incrementCatalogCount(self):
        # catalog_count is a minimal counter object that we will increment 
        # every time an object is indexed/reindexed/unindexed -- we will
        # then use this for cache invalidation
        if self._catalog_count is None:
            self._catalog_count = Length.Length()
        self._catalog_count.change(1)
        self.updateChangeDate()

    def getCatalogCount(self):
        return self._catalog_count()

    def incrementPermissionCount(self):
        # permission_count is a minimal counter object that we will increment every
        # time the relationship between roles and permissions changes.  We will use
        # this value for cache invalidation
        if self._permission_count is None:
            self._permission_count = Length.Length()
        self._permission_count.change(1)
        self.updateChangeDate()

    def getPermissionCount(self):
        if self._permission_count is None:
            self._permission_count = Length.Length()
        return self._permission_count()

    # ##### Accessors, mutators, and helper methods used in configuration ######

    def _getCompleteUrl(self, url):
        if url.find('//') == -1:
            url = 'http://' + url
        p = urlparse.urlparse(url)
        protocol = p[0]
        if not protocol:
            protocol = 'http'
        host = p[1]
        split_host = host.split(':')
        if len(split_host) == 1:
            if protocol == 'https':
                port = '443'
            else:
                port = '80'
            host = split_host[0] + ':' + port
        return urlparse.urlunparse((protocol, host, '','','',''))

    def _getSquidUrls(self):
        # get a list of urls from squid
        squid_tool = getToolByName(self, 'portal_squid')
        return tuple([url for url in squid_tool.getSquidURLs().split('\n') if url])
        
    def _setSquidUrls(self, list_of_urls):
        # pass a \n-joined list of urls to squid tool
        squid_tool = getToolByName(self, 'portal_squid')
        squid_tool.manage_setSquidSettings('\n'.join(list_of_urls))

    def hasPurgeableProxy(self):
        # return self.getCacheConfig() in ('squid', 'squid_behind_apache')
        return self.getProxyPurgeConfig() != 'no-purge'

    def getDomains(self):
        if self.getProxyPurgeConfig() in ('vhm-rewrite','custom-rewrite'):
            return self.getField('domains').get(self)
        else:
            return self._getSquidUrls()

    security.declareProtected(permissions.ManagePortal, 'setDomains')
    def setDomains(self, value):
        if value is None:
            value = ''
        if type(value) == type(''):
            value = value.replace('\r','\n')
            value = value.split('\n')
        value = [v.strip() for v in value if v]
        domains = []
        for v in value:
            domains.append(self._getCompleteUrl(v))
        if self.getProxyPurgeConfig() in ('vhm-rewrite','custom-rewrite'):
            self.getField('domains').set(self, domains)
        else:
            self._setSquidUrls(domains)

    security.declareProtected(permissions.View, 'getSquidURLs')
    def getSquidURLs(self):
        if self.getProxyPurgeConfig() in ('vhm-rewrite','custom-rewrite'):
            return self._getSquidUrls()
        else:
            return ''

    security.declareProtected(permissions.ManagePortal, 'setSquidURLs')
    def setSquidURLs(self, value):
        if self.getProxyPurgeConfig() in ('vhm-rewrite','custom-rewrite'):
            if value is None:
                value = ''
            if type(value) == type(''):
                value = value.replace('\r','\n')
                value = value.split('\n')
            self._setSquidUrls([self._getCompleteUrl(v) for v in value if v])

    security.declareProtected(permissions.ManagePortal, 'setVaryHeader')
    def setVaryHeader(self, value):
        # Correct for missing headers 
        values = [v.strip() for v in value.split(',')]
        request = aq_get(self, 'REQUEST', None)
        if request is not None:
            gzip = request.get('gzip',None)
        else:
            gzip = self.getGzip()
        if gzip in ('accept-encoding', 'accept-encoding+user-agent'):
            if not 'Accept-Encoding' in values:
                values.append('Accept-Encoding')
            if gzip == 'accept-encoding+user-agent':
                if not 'User-Agent' in values:
                    values.append('User-Agent')
        value = ', '.join(values)
        self.getField('varyHeader').set(self, value)

    def post_validate(self, REQUEST, errors):
        proxy_purge_config = REQUEST.get('proxyPurgeConfig',None)
        squid_urls = REQUEST.get('squidURLs',None)
        if proxy_purge_config in ('vhm-rewrite','custom-rewrite'):
            if not squid_urls:
                errors['squidURLs'] = 'Please enter the URLs for your proxy caches.  We need this to generate the URLs for PURGE requests.'
        else:
            if squid_urls:
                errors['squidURLs'] = 'Set this field only if rewriting proxy cache PURGE requests'

        if proxy_purge_config in ('no-rewrite','vhm-rewrite','custom-rewrite'):
            if not REQUEST.get('domains', None):
                errors['domains'] = 'Please enter the domains that you will be caching. We need this to generate proper PURGE requests.'

        # Not needed anymore since setVaryHeader fixes itself if necessary
        #gzip = REQUEST.get('gzip',None)
        #vary_header = REQUEST.get('varyHeader','')
        #values = [v.strip() for v in vary_header.split(',')]
        #if gzip in ('accept-encoding', 'accept-encoding+user-agent'):
        #    if not 'Accept-Encoding' in values:
        #        errors['varyHeader'] = 'When Compression is set to "%s", you need "Accept-Encoding" in the Vary header' % gzip
        #    if gzip == 'accept-encoding+user-agent':
        #        if not 'User-Agent' in values:
        #            errors['varyHeader'] = 'When Compression is set to %s, you need "User-Agent" in the Vary header' % gzip

    security.declareProtected(permissions.ManagePortal, 'manage_purgePageCache')
    def manage_purgePageCache(self, REQUEST=None):
        """Purge the page cache manager"""
        msg = 'portal_status_message=Page+cache+not+purged:+CacheFu+disabled'
        if self.getEnabled():
            pc = getToolByName(self, config.PAGE_CACHE_MANAGER_ID)
            pc.manage_purge()
            msg = 'portal_status_message=Page+cache+purged'
        if REQUEST is not None:
            url = REQUEST.get('HTTP_REFERER', self.absolute_url()+'/edit')
            if url.find('?') != -1:
                url += '&' + msg
            else:
                url += '?' + msg
            return REQUEST.RESPONSE.redirect(url)

    # ##### Helper methods used for building ETags and for header setting ######

    def canAnonymousView(self, object):
        """Returns True if anonymous users can view an object"""
        if 'Anonymous' in rolesForPermissionOn('View', object):
            return True
        # XXX i am not sure it is possible to assign local roles to the anonymous user
        # XXX if it is, there may need to be some local role tomfoolery here
        # XXX something like the following
        # roles_with_view = {}
        # for r in rolesForPermissionOn('View', obj):
        #    roles_with_view[r] = 1
        # try:
        #    all_local_roles = portal.acl_users._getAllLocalRoles(obj)
        # except AttributeError:
        #    all_local_roles = _mergedLocalRoles(obj)
        # if 'Anonymous user' in all_local_roles:
        #    for r in all_local_roles['Anonymous user']:
        #       if r in roles_with_view:
        #          return True
        return False

    security.declarePublic('isGzippable')
    def isGzippable(self, css=0, js=0, REQUEST=None):
        """Indicate whether gzipping is allowed for the current request.  Returns
           a tuple.  The first argument indicates whether gzipping should be enabled,
           the second indicates whether gzipping should be forced, and the third
           whether the browser will accept gzipped content."""
        # force: force http compression even if the browser doesn't send an accept
        # debug: return compression state (0: no, 1: yes, 2: force)
        # css: set this to 1 inside a css file (for later use)
        # js: set this to 1 inside a js file (for later use)

        if REQUEST is None:
            REQUEST = self.REQUEST
        use_gzip = self.getGzip()
        if not self.getEnabled():
            use_gzip = 'never'

        force = 0
        if use_gzip == 'never':
            enable_compression = 0
        elif use_gzip == 'always':
            enable_compression = 1
            force = 1
        elif use_gzip == 'accept-encoding':
            # compress everything except css and js
            enable_compression = 1
        elif use_gzip == 'accept-encoding+user-agent':
            # gzip compatibility info courtesy of
            # http://httpd.apache.org/docs/2.2/mod/mod_deflate.html
            user_agent = REQUEST.get('HTTP_USER_AGENT', '')
            if user_agent.startswith('Mozilla/4'):
                # Netscape 4.x can't handle gzipped css and js
                enable_compression = (css==0 and js==0)
            # Netscape 4.0.6-4.0.8 has some gzip-related bugs
            if user_agent[len('Mozilla/4.')] in ('6','7','8'):
                enable_compression = 0
            # Some versions of MSIE pretend to be Netscape 4.x but are OK with gzipping
            if user_agent.find('MSIE'):
                enable_compression = 1

        return (enable_compression, force, REQUEST.get('HTTP_ACCEPT_ENCODING', '').find('gzip') != -1)

    # ##### Main methods ######

    security.declarePublic('getRuleAndHeaderSet')
    def getRuleAndHeaderSet(self, request, object, view, member):
        """Get the caching rule that applies here and the header set specified by the rule"""
        if not self.getEnabled():
            return (None, None)
        rules = self.getRules().objectValues()
        for rule in rules:
            try:
                header_set = rule.getHeaderSet(request, object, view, member)
                if header_set is not None:
                    return (rule, header_set)
            except ConflictError:
                raise
            except:
                log_exc()
        return (None, None)

    security.declarePublic('getUrlsToPurge')
    def getUrlsToPurge(self, object):
        """Get a list of URLs to be purged when the given object is added / modified / deleted"""

        # if nothing to purge or cachefu disabled, return an empty list
        if not self.hasPurgeableProxy() or not self.getEnabled():
            return []
        
        relative_urls = sets.Set()
        rules = self.getRules().objectValues()
        for rule in rules:
            try:
                rule.getRelativeUrlsToPurge(object, relative_urls)
            except ConflictError:
                raise
            except:
                log_exc()

        for adapter in zope.component.subscribers([aq_inner(object)], IPurgeUrls):
            relative_urls.union_update(adapter.getRelativeUrls())

        relative_urls = list(relative_urls)

        absolute_urls=[]
        for adapter in zope.component.subscribers([aq_inner(object)], IPurgeUrls):
            absolute_urls.extend(adapter.getAbsoluteUrls(relative_urls))

        if relative_urls:
            proxy_purge_config = self.getProxyPurgeConfig()
            if proxy_purge_config == 'vhm-rewrite':
                # unless defined otherwise, we assume urls passed to the cache proxy
                # are of the standard form expected by the VirtualHostMonster:
                # [squid_url]/VirtualHostBase/[protocol]/[host]:[port]/[path to portal root]/VirtualHostRoot/[path]
                url_tool = getToolByName(self, 'portal_url')
                portal_path = '/'.join(url_tool.getPortalObject().getPhysicalPath())
                domains = self.getDomains()
                prefixes = []
                for d in domains:
                    p = urlparse.urlparse(d)
                    protocol = p[0]
                    host = p[1]
                    split_host = host.split(':')
                    host = split_host[0]
                    port = split_host[1]
                    prefixes.append('VirtualHostBase/%s/%s:%s%s/VirtualHostRoot/' \
                                     % (protocol, host, port, portal_path))
                relative_urls = [prefix+url for prefix in prefixes for url in relative_urls]
            elif proxy_purge_config == 'custom-rewrite':
                domains = [urlparse.urlparse(d) for d in self.getDomains()]
                relative_urls = self.rewritePurgeUrls(relative_urls, domains)


        return relative_urls + absolute_urls 

    # A few helper methods
    
    def getMember(self):
        """Utility method for getting a member for use in expression contexts.  Returns
           the Member object for the currently authenticated member or None if the
           user is not authenticated."""
        pm = getToolByName(self, 'portal_membership', None)
        # stick to the CachingPolicyManager expression convention
        if not pm or pm.isAnonymousUser():
            return None 
        else:
            return pm.getAuthenticatedMember()
        
    # a few methods for generating non-hideous default ids
    security.declareProtected(permissions.ManagePortal, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        context = self.REQUEST.PARENTS[0]
        question_ids = context.objectIds()
        n = len(question_ids)+1
        while str(n) in question_ids:
            n = n + 1
        return str(n)

    def _isIDAutoGenerated(self, id):
        try:
            int(id)
            return True
        except:
            return False
        
registerType(CacheTool, config.PROJECT_NAME)
