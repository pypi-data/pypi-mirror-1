# This Python file uses the following encoding: utf-8
"""
content cache rule implementation tests

$Id: test_content_cache_rule.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.interfaces import ICacheRule

class TestContentCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('ContentCacheRule', self.folder, 'ccr')
        self.ccr = getattr(self.folder, 'ccr')

    def _testImplementsBaseCacheRule(self):
        # I need to test this
        iface = IBaseCacheRule
        self.failUnless(iface.isImplementedBy(self.ccr))
        self.failUnless(verifyObject(iface, self.ccr))

    def testTypeInfo(self):
        ti = self.ccr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Content Cache Rule')
        self.failUnlessEqual(ti.getId(), 'ContentCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'ContentCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config',
                                                      'view': 'cache_policy_item_config',
                                                      'edit': 'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        ccr = ttool['ContentCacheRule']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, ccr.getActionInfo, actions)
        self.setRoles(['Manager', 'Member'])
        info = ccr.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestContentCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('ContentCacheRule', self.folder, 'ccr')
        self.ccr = getattr(self.folder, 'ccr')

    def test_getPurgeExpression(self):
        # check if returns default value
        self.failUnlessEqual(self.ccr.getPurgeExpression(), '')

    def test_setPurgeExpression(self):
        self.ccr.setPurgeExpression('python:2+2')
        self.failUnlessEqual(self.ccr.getPurgeExpression(), 'python:2+2')
        self.ccr.setVaryExpression(None)
        self.failUnlessEqual(self.ccr.getVaryExpression(), '')

    def _test_validate_purgeExpression(self):
        self.fail('not yet implemented...')

    def _test_getPurgeExpressionValue(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSet(self):
        self.fail('not yet implemented...')

    def _test_getViewsUrlsForObject(self):
        self.fail('not yet implemented...')

    def _test_getObjectFieldUrls(self):
        self.fail('not yet implemented...')

    def _test_getRelativeUrlsToPurge(self):
        self.fail('not yet implemented...')

    # This looks fragile. Seems like it would break with
    # every new Plone version
    def _test_getContentTypesVocabulary(self):
        """ check if returns default content types """
        types = (
            ('CMF Document', 'CMF Document'),
            ('CMF Event', 'CMF Event'),
            ('CMF Favorite', 'CMF Favorite'),
            ('CMF File', 'CMF File'),
            ('CMF Folder', 'CMF Folder'),
            ('CMF Image', 'CMF Image'),
            ('CMF Large Plone Folder', 'CMF Large Plone Folder'),
            ('CMF Link', 'CMF Link'),
            ('CMF News Item', 'CMF News Item'),
            ('CMF Topic', 'CMF Topic'),
            ('Discussion Item', 'Discussion Item'),
            ('Event', 'Event'),
            ('Favorite', 'Favorite'),
            ('File', 'File'),
            ('Folder', 'Folder'),
            ('Image', 'Image'),
            ('Large Plone Folder', 'Large Folder (Large Plone Folder)'),
            ('Link', 'Link'),
            ('News Item', 'News Item'),
            ('Document', 'Page (Document)'),
            ('Plone Site', 'Plone Site'),
            ('Topic', 'Smart Folder (Topic)')
        )

        for t in self.ccr.getContentTypesVocabulary().items():
            self.failUnless(t in types)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentCacheRule))
    suite.addTest(makeSuite(TestContentCacheRuleMethods))
    return suite
