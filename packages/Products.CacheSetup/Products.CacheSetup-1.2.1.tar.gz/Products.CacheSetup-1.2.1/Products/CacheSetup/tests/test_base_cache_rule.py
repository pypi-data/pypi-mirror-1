# This Python file uses the following encoding: utf-8
"""
base cache rule implementation tests

$Id: test_base_cache_rule.py 86306 2009-05-17 23:15:20Z newbery $
"""

__author__ = 'Héctor Velarde <hvelarde@jornada.com.mx>'
__docformat__ = 'restructuredtext'

from base import CacheFuTestCase

from Interface.Verify import verifyObject
from Products.Archetypes.interfaces import IBaseContent
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.content.base_cache_rule import BaseCacheRule
from Products.CacheSetup.content.nocatalog import NoCatalog
from Products.CacheSetup.interfaces import ICacheRule

class TestBaseCacheRule(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('BaseCacheRule', self.folder, 'bcr')
        self.bcr = getattr(self.folder, 'bcr')

    def testIsNoCatalog(self):
        self.failUnless(isinstance(self.bcr, NoCatalog))

    def testImplementsCacheRule(self):
        iface = ICacheRule
        self.failUnless(iface.isImplementedBy(self.bcr))
        self.failUnless(verifyObject(iface, self.bcr))

    def testImplementsBaseContent(self):
        iface = IBaseContent
        self.failUnless(iface.isImplementedBy(self.bcr))
        self.failUnless(verifyObject(iface, self.bcr))

    def testTypeInfo(self):
        ti = self.bcr.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Base Cache Rule')
        self.failUnlessEqual(ti.getId(), 'BaseCacheRule')
        self.failUnlessEqual(ti.Metatype(), 'BaseCacheRule')
        self.failUnlessEqual(ti.globalAllow(), 0)

class TestBaseCacheRuleMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('BaseCacheRule', self.folder, 'bcr')
        self.bcr = getattr(self.folder, 'bcr')

    def _test_validate_expression(self):
        self.fail('not yet implemented...')

    def _test_getPredicateExpression(self):
        self.fail('not yet implemented...')

    def _test_setPredicateExpression(self):
        self.fail('not yet implemented...')

    def _test_validate_predicateExpression(self):
        self.fail('not yet implemented...')

    def _test_testPredicate(self):
        self.fail('not yet implemented...')

    def _test_getEtagExpression(self):
        self.fail('not yet implemented...')

    def _test_setEtagExpression(self):
        self.fail('not yet implemented...')

    def _test_validate_etagExpression(self):
        self.fail('not yet implemented...')

    def _test_getEtagExpressionValue(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSetIdExpression(self):
        self.fail('not yet implemented...')

    def _test_setHeaderSetIdExpression(self):
        self.fail('not yet implemented...')

    def _test_validate_headerSetIdExpression(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSetIdExpressionValue(self):
        self.fail('not yet implemented...')

    def test_getLastModifiedExpression(self):
        # check if returns default value
        self.failUnlessEqual(self.bcr.getLastModifiedExpression(), 'python:object.modified()')

    def test_setLastModifiedExpression(self):
        self.bcr.setLastModifiedExpression(None)
        self.failUnlessEqual(self.bcr.getLastModifiedExpression(), '')
        self.bcr.setLastModifiedExpression('python:object.modified()')
        self.failUnlessEqual(self.bcr.getLastModifiedExpression(), 'python:object.modified()')

    def _test_validate_lastModifiedExpression(self):
        self.fail('not yet implemented...')

    def _test_getLastModified(self):
        self.fail('not yet implemented...')

    def _test_lastDate(self):
        self.fail('not yet implemented...')

    def _test_getLastTransactionDate(self):
        self.fail('not yet implemented...')

    def test_getVaryExpression(self):
        # check if returns default value
        self.failUnlessEqual(self.bcr.getVaryExpression(), 'python:rule.portal_cache_settings.getVaryHeader()')

    def test_setVaryExpression(self):
        self.bcr.setVaryExpression(None)
        self.failUnlessEqual(self.bcr.getVaryExpression(), '')
        self.bcr.setVaryExpression('python:rule.portal_cache_settings.getVaryHeader()')
        self.failUnlessEqual(self.bcr.getVaryExpression(), 'python:rule.portal_cache_settings.getVaryHeader()')

    def _test_validate_varyExpression(self):
        self.fail('not yet implemented...')

    def _test_getVary(self):
        self.fail('not yet implemented...')

    def _test_getExpressionContext(self):
        self.fail('not yet implemented...')

    def _test_associateTemplate(self):
        self.fail('not yet implemented...')

    def _test_getHeaderSet(self):
        self.fail('not yet implemented...')

    def test_getHeaderSetVocabulary(self):
        """ check if returns default header set vocabulary """
        # where is this thing defined?
        types = (
            ('expression', 'Use expression below'),
            ('no-cache', 'Do not cache'),
            ('cache-in-memory', 'Cache in Memory'),
            ('cache-with-etag', 'Cache with ETag'),
            ('cache-with-last-modified', 'Cache file with Last-Modified'),
            ('cache-in-proxy-1-hour', 'Cache in proxy cache for 1 hour'),
            ('cache-in-proxy-24-hours', 'Cache in proxy cache for 24 hours'),
            ('cache-in-browser-1-hour', 'Cache in browser for 1 hour'),
            ('cache-in-browser-24-hours', 'Cache in browser for 24 hours'),
            ('cache-in-browser-forever', 'Cache in browser forever'),
            ('None', 'Rule does not apply')
        )

        for t in self.bcr.getHeaderSetVocabulary().items():
            self.failUnless(t in types)

    def test_getObjectDefaultView(self):
        """ check if standard Plone types return their default views """
        types = (
            ('Document', 'document_view'),
            ('Event', 'event_view'),
            ('Favorite', 'favorite_view'),
            ('File', 'index_html'),
            ('Folder', 'folder_listing'),
            ('Image', 'index_html'),
            ('Link', 'link_view'),
            ('News Item', 'newsitem_view'),
        )

        for type, view in types:
            self.folder.invokeFactory(type, type)
            obj = getattr(self.folder, type)
            self.failUnlessEqual(self.bcr.getObjectDefaultView(obj), view)
            self.folder.manage_delObjects(type)

    def _test_addEtagComponent(self):
        self.fail('not yet implemented...')

    def _test_getEtag(self):
        self.fail('not yet implemented...')

    def _test_getRelativeUrlsToPurge(self):
        self.fail('not yet implemented...')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBaseCacheRule))
    suite.addTest(makeSuite(TestBaseCacheRuleMethods))
    return suite
