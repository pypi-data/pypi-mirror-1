# This Python file uses the following encoding: utf-8
"""
rule folder implementation tests

$Id: test_rule_folder.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject

from Products.Archetypes.atapi import OrderedBaseFolder
from Products.Archetypes.interfaces.base import IBaseFolder
from Products.CMFCore.interfaces.Dynamic import DynamicType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.OrderedContainer import IOrderedContainer
from Products.CMFPlone.utils import _createObjectByType
from OFS.IOrderSupport import IOrderedContainer as IZopeOrderedContainer

from Products.CacheSetup.config import *
from Products.CacheSetup.content.nocatalog import NoCatalog
from Products.CacheSetup.interfaces import ICacheToolFolder

class TestRuleFolder(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('RuleFolder', self.folder, 'rf')
        self.rf = getattr(self.folder, 'rf')

    def testIsNoCatalog(self):
        self.failUnless(isinstance(self.rf, NoCatalog))

    def testImplementsOrderedBaseFolder(self):
        # OrderedBaseFolder is made of all of this things
        iface = IOrderedContainer
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))
        iface = IZopeOrderedContainer
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))
        iface = IBaseFolder
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))
        iface = DynamicType
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))

    def testImplementsCacheToolFolder(self):
        iface = ICacheToolFolder
        self.failUnless(iface.isImplementedBy(self.rf))
        self.failUnless(verifyObject(iface, self.rf))

    def testTypeInfo(self):
        ti = self.rf.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Rule Folder')
        self.failUnlessEqual(ti.getId(), 'RuleFolder')
        self.failUnlessEqual(ti.Metatype(), 'RuleFolder')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config', \
                                                      'view': 'cache_policy_item_config', \
                                                      'edit': 'cache_policy_item_config'})

    def testAllowedContentTypes(self):
        allowed = ('ContentCacheRule','TemplateCacheRule','PolicyHTTPCacheManagerCacheRule')
        for t in self.rf.allowedContentTypes():
            self.failUnless(t.getId() in allowed)

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        rf = ttool['RuleFolder']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, rf.getActionInfo, actions)
        self.setRoles(['Manager','Member'])
        info = rf.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleFolder))
    return suite
