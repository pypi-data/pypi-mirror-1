# This Python file uses the following encoding: utf-8
"""
policy http cache manager cache rule implementation tests

$Id: test_phcm_cache_rule.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *

class TestPolicyHTTPCacheManagerCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('PolicyHTTPCacheManagerCacheRule', self.folder, 'phcmcr')
        self.phcmcr = getattr(self.folder, 'phcmcr')

    def _testImplementsBaseCacheRule(self):
        # I need to test this
        iface = IBaseCacheRule
        self.failUnless(iface.isImplementedBy(self.phcmcr))
        self.failUnless(verifyObject(iface, self.phcmcr))

    def testTypeInfo(self):
        ti = self.phcmcr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'PolicyHTTPCacheManager Cache Rule')
        self.failUnlessEqual(ti.getId(), 'PolicyHTTPCacheManagerCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'PolicyHTTPCacheManagerCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config',
                                                      'view': 'cache_policy_item_config',
                                                      'edit': 'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        phcmcr = ttool['PolicyHTTPCacheManagerCacheRule']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, phcmcr.getActionInfo, actions)
        self.setRoles(['Manager', 'Member'])
        info = phcmcr.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestPolicyHTTPCacheManagerCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('PolicyHTTPCacheManagerCacheRule', self.folder, 'phcmcr')
        self.phcmcr = getattr(self.folder, 'phcmcr')

    def _test_getContentTypesVocabulary(self):
        self.fail('not yet implemented...')
    
    def _test_getPolicyHTTPCacheManagerVocabulary(self):
        self.fail('not yet implemented...')

    def _test_getEtag(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSet(self, request, object, view, member):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPolicyHTTPCacheManagerCacheRule))
    suite.addTest(makeSuite(TestPolicyHTTPCacheManagerCacheRuleMethods))
    return suite
