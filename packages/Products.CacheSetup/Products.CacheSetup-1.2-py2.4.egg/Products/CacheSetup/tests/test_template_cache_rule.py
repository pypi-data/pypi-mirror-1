# This Python file uses the following encoding: utf-8
"""
template cache rule implementation tests

$Id$
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *

class TestTemplateCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('TemplateCacheRule', self.folder, 'tcr')
        self.tcr = getattr(self.folder, 'tcr')

    def _testImplementsBaseCacheRule(self):
        # I need to test this
        iface = IBaseCacheRule
        self.failUnless(iface.isImplementedBy(self.tcr))
        self.failUnless(verifyObject(iface, self.tcr))

    def testTypeInfo(self):
        ti = self.tcr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Template Cache Rule')
        self.failUnlessEqual(ti.getId(), 'TemplateCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'TemplateCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config',
                                                      'view': 'cache_policy_item_config',
                                                      'edit': 'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        tcr = ttool['TemplateCacheRule']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, tcr.getActionInfo, actions)
        self.setRoles(['Manager', 'Member'])

        info = tcr.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestTemplateCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        self.tool = self.portal.portal_cache_settings

    def _test_getHeaderSet(self):
        # this can be implemented against default rules
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateCacheRule))
    suite.addTest(makeSuite(TestTemplateCacheRuleMethods))
    return suite
