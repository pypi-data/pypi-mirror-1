# This Python file uses the following encoding: utf-8
"""
cache tool implementation tests

$Id: test_cache_tool.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.CMFCore.utils import getToolByName, UniqueObject

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheTool

class TestCacheTool(CacheFuTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.folder, CACHE_TOOL_ID)

    def testIsUniqueObject(self):
        """ a tool has to be an UniqueObject """
        self.failUnless(isinstance(self.tool, UniqueObject))

    def testImplementsBaseFolder(self):
        iface = IBaseFolder
        self.failUnless(iface.providedBy(self.tool))
        self.failUnless(verifyObject(iface, self.tool))

    def testImplementsCacheTool(self):
        iface = ICacheTool
        self.failUnless(iface.providedBy(self.tool))
        self.failUnless(verifyObject(iface, self.tool))

    def testTypeInfo(self):
        ti = self.tool.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Cache Configuration Tool')
        self.failUnlessEqual(ti.getId(), 'CacheTool')
        self.failUnlessEqual(ti.Metatype(), 'CacheTool')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_tool_config',
                                                      'view' : 'cache_tool_config',
                                                      'edit': 'base_edit'})

    def testAllowedContentTypes(self):
        allowed = ('CachePolicy',)
        for t in self.tool.allowedContentTypes():
            self.failUnless(t.getId() in allowed)

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        tool = ttool['CacheTool']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, tool.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = tool.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestCacheToolMethods(CacheFuTestCase):

    def afterSetUp(self):
        self.tool = getattr(self.folder, CACHE_TOOL_ID)

    def _test_initializeArchetype(self):
        self.fail('not yet implemented...')

    # The ActivePolicy vocabulary is likely to change with each release
    # There probably should be a better way to keep track of these instead
    # of hard coding the list in the test
    def _test_getActivePolicyVocabulary(self):
        """ check against default active policy vocabulary """
        vocab = (
            ('default-cache-policy', 'Default Cache Policy'),
            ('no-proxy-cache', 'No Proxy Cache'),
            ('default-cache-policy-v2', 'Default Cache Policy, slightly improved'),
            ('squid-without-vary', 'Squid without Vary header (Note: Turn off compression)')
        )
        for i in self.tool.getActivePolicyVocabulary().items():
            self.failUnless(i in vocab)
        # what about testing for self.tool.getActivePolicyVocabulary(display=1)

    def test_getActivePolicyId(self):
        self.failUnlessEqual(self.tool.getActivePolicyId(), DEFAULT_POLICY_ID)
        # need to test this after erasing the default one

    def _test_setDisplayPolicy(self):
        self.fail('not yet implemented...')

    def _test_setEnabled(self):
        self.fail('not yet implemented...')

    def _test_getPolicy(self):
        self.fail('not yet implemented...')

    def _test_getDisplayPolicy(self):
        self.fail('not yet implemented...')

    # The details of the cache policies are subject to change with each release
    # There probably should be a better way to keep track of this instead of
    # hard coding the lists in the tests
    def _test_getRules(self):
        """ test rules for all policies """
        # right now all policies have the same rules
        rules = (
            'httpcache', 'plone-content-types', 'plone-containers',
            'plone-templates', 'resource-registries', 'downloads', 'dtml-css'
        )
        ids = (None, ) + POLICY_IDS # None is for default
        for id in ids:
            for r, t in self.tool.getRules(policy_id=id).items():
                self.failUnless(r in rules)
                # what to test against t?

    # The details of the cache policies are subject to change with each release
    # There probably should be a better way to keep track of this instead of
    # hard coding the lists in the tests
    def _test_getHeaderSets(self):
        """ test header sets for all policies """
        # right now all policies have the same header sets
        header_sets = (
            'no-cache', 'cache-in-memory', 'cache-with-etag',
            'cache-with-last-modified', 'cache-in-proxy-1-hour',
            'cache-in-proxy-24-hours', 'cache-in-browser-1-hour',
            'cache-in-browser-24-hours', 'cache-in-browser-forever'
        )
        ids = (None, ) + POLICY_IDS # None is for default
        for id in ids:
            for hs, t in self.tool.getHeaderSets(policy_id=id).items():
                self.failUnless(hs in header_sets)
                # what to test against t?

    def _test_getHeaderSetById(self):
        self.fail('not yet implemented...')

    def _test_addPolicyFolder(self):
        self.fail('not yet implemented...')

    def _test_addRulesFolder(self):
        self.fail('not yet implemented...')

    def _test_addHeaderSetsFolder(self):
        self.fail('not yet implemented...')

    def _test_incrementCatalogCount(self):
        self.fail('not yet implemented...')

    def _test_getCatalogCount(self):
        self.fail('not yet implemented...')

    def _test_incrementPermissionCount(self):
        self.fail('not yet implemented...')

    def _test_getPermissionCount(self):
        self.fail('not yet implemented...')

    def _test_getCompleteUrl(self):
        self.fail('not yet implemented...')

    def _test_getSquidUrls(self):
        self.fail('not yet implemented...')

    def _test_setSquidUrls(self):
        self.fail('not yet implemented...')

    def _test_getCompleteUrl(self):
        self.fail('not yet implemented...')

    def _test_hasPurgeableProxy(self):
        self.fail('not yet implemented...')

    def _test_getDomains(self):
        self.fail('not yet implemented...')

    def _test_setDomains(self):
        self.fail('not yet implemented...')

    def _test_getSquidURLs(self):
        self.fail('not yet implemented...')

    def _test_setSquidURLs(self):
        self.fail('not yet implemented...')

    def _test_post_validate(self):
        self.fail('not yet implemented...')

    def _test_manage_purgePageCache(self):
        self.fail('not yet implemented...')

    def _test_canAnonymousView(self):
        self.fail('not yet implemented...')

    def _test_isGzippable(self):
        self.fail('not yet implemented...')

    def _test_getRuleAndHeaderSet(self):
        self.fail('not yet implemented...')

    def _test_getUrlsToPurge(self):
        self.fail('not yet implemented...')

    def _test_getMember(self):
        self.fail('not yet implemented...')

    def _test_generateUniqueId(self):
        self.fail('not yet implemented...')

    def _test_isIDAutoGenerated(self):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCacheTool))
    suite.addTest(makeSuite(TestCacheToolMethods))
    return suite
