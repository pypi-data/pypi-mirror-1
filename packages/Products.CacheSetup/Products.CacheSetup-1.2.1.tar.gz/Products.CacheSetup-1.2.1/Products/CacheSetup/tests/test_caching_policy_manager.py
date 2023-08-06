# This Python file uses the following encoding: utf-8
"""
caching policy manager implementation tests

$Id: test_caching_policy_manager.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from Interface.Verify import verifyObject
from Products.CMFCore.interfaces import ICachingPolicyManager

from Products.CacheSetup.config import *
from Products.CacheSetup.content.caching_policy_manager import CSCachingPolicyManager

# this thing is pretty obscure to me so tests are incomplete

class TestCachingPolicyManager(CacheFuTestCase):

    def afterSetUp(self):
        self.cpm = CSCachingPolicyManager()

    def testImplementsCachingPolicyManager(self):
        iface = ICachingPolicyManager
        self.failUnless(iface.isImplementedBy(self.cpm))
        self.failUnless(verifyObject(iface, self.cpm))

class TestCachingPolicyManagerMethods(CacheFuTestCase):

    def afterSetUp(self):
        self.cpm = CSCachingPolicyManager()

    def _test_getHeadersToAddAndRemove(self):
        self.fail('not yet implemented...')

    def _test_getHTTPCachingHeaders(self):
        self.fail('not yet implemented...')

    def _test_getModTimeAndETag(self):
        self.fail('not yet implemented...')

    def _test_getETag(self):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCachingPolicyManager))
    suite.addTest(makeSuite(TestCachingPolicyManagerMethods))
    return suite
