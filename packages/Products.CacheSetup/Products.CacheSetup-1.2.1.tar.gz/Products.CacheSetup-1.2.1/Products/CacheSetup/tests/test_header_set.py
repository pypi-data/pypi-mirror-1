# This Python file uses the following encoding: utf-8
"""
header set implementation tests

$Id: test_header_set.py 86306 2009-05-17 23:15:20Z newbery $
"""

from base import CacheFuTestCase

from AccessControl import Unauthorized
from Interface.Verify import verifyObject
from Products.Archetypes.interfaces.base import IBaseContent
from Products.CMFCore.utils  import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from Products.CacheSetup.config import *
from Products.CacheSetup.content.nocatalog import NoCatalog

class TestHeaderSet(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('HeaderSet', self.folder, 'hs')
        self.hs = getattr(self.folder, 'hs')

    def testIsNoCatalog(self):
        self.failUnless(isinstance(self.hs, NoCatalog))

    def testImplementsBaseContent(self):
        iface = IBaseContent
        self.failUnless(iface.isImplementedBy(self.hs))
        self.failUnless(verifyObject(iface, self.hs))

    def testTypeInfo(self):
        ti = self.hs.getTypeInfo()
        self.failUnlessEqual(ti.Title(), 'Response Header Set')
        self.failUnlessEqual(ti.getId(), 'HeaderSet')
        self.failUnlessEqual(ti.Metatype(), 'HeaderSet')
        self.failUnlessEqual(ti.globalAllow(), 0)
        self.failUnlessEqual(ti.getMethodAliases(), {'(Default)': 'cache_policy_item_config',
                                                      'view': 'cache_policy_item_config',
                                                      'edit': 'cache_policy_item_config'})

    def testActions(self):
        # not pretty sure about this
        actions = ('object/view',)
        ttool = getToolByName(self.portal, 'portal_types')
        hs = ttool['HeaderSet']
        # actions have ManagePortal permission set
        self.assertRaises(Unauthorized, hs.getActionInfo, actions)
        self.setRoles(['Manager', 'Member'])
        info = hs.getActionInfo(actions)
        self.failUnless(info is not None)
        self.failUnlessEqual(info['url'], '')

class TestHeaderSetMethods(CacheFuTestCase):

    def afterSetUp(self):
        _createObjectByType('HeaderSet', self.folder, 'hs')
        self.hs = getattr(self.folder, 'hs')

    def _test_validate_expression(self):
        self.fail('not yet implemented...')

    def _test_getLastModifiedValue(self):
        self.fail('not yet implemented...')

    def _test_getVaryValue(self):
        self.fail('not yet implemented...')

    def _test_getPageCacheKey(self):
        self.fail('not yet implemented...')

    def _test_getEtagValue(self):
        self.fail('not yet implemented...')

    def _test_getEtagValue(self):
        self.fail('not yet implemented...')

    def _test_getHeaders(self):
        self.fail('not yet implemented...')

from App.Common import rfc1123_date

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o

class TestHeaderSetOld(CacheFuTestCase):
    USER1 = 'user1'
    
    def afterSetUp(self):
        CacheFuTestCase.afterSetUp(self)
        
        # Add a couple of users
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser(self.USER1, 'secret', ['Member'], [])
        self.login('manager')

        self.portal.portal_quickinstaller.installProducts(['CacheSetup'])

        # We have added a skin so we need to rebuild the skin object
        # (since the object is cached in the current request)
        self._refreshSkinData()

        self.folder.invokeFactory(id='doc', type_name='Document')
        pcs = self.portal.portal_cache_settings
        pcs.setEnabled(True)

        headers = pcs.getHeaderSets()
        headers.invokeFactory(id='my_hs', type_name='HeaderSet')
        rules = pcs.getRules()
        rules.invokeFactory(id='my_rule', type_name='ContentCacheRule')

    def test_get_etag(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member)

        rule.setEtagComponents(['expression'])
        rule.setEtagExpression('string:my_etag')
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(None)

        h.setEtag(True)
        self.assertEqual(h.getEtagValue(expr_context), '|my_etag')
        h.setEtag(False)
        self.assertEqual(h.getEtagValue(expr_context), None)

    def _getCacheControl(self, hdrs):
        d = self._parseHeaders(hdrs[0])
        cc = d['Cache-control']
        cc = [cc.strip() for cc in cc.split(',')]
        d = {}
        for part in cc:
            sp = part.split('=')
            token = sp[0].strip()
            if len(sp) > 1:
                value = sp[1]
            else:
                value = None
            self.failIf(d.has_key(token))
            d[token] = value
        return d

    def _parseHeaders(self, hdrs):
        d = {}
        for (k,v) in hdrs:
            self.failUnless(not d.has_key(k))
            d[k] = v
        return d

    def test_headers_last_modified(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member)

        h.setLastModified('delete')
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        self.assertEqual(headers_to_remove, ['Last-modified'])
        h.setLastModified('no')
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        self.assertEqual(headers_to_remove, [])
        self.failUnless('Last-modified' not in [hdr[0] for hdr in headers_to_add])
        h.setLastModified('yes')
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        self.assertEqual(headers_to_remove, [])
        d = self._parseHeaders(headers_to_add)
        self.failUnless(d.has_key('Last-modified'))
        mod_time = rfc1123_date(doc.modified().timeTime())
        self.failUnlessEqual(d['Last-modified'], mod_time)

    def test_headers_etag(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member)

        rule.setEtagComponents(['expression'])
        rule.setEtagExpression('string:my_etag')
        rule.setEtagRequestValues([])
        rule.setEtagTimeout(None)

        h.setEtag(True)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.assertEqual(d['ETag'], '|my_etag')
        h.setEtag(False)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.failIf(d.has_key('ETag'))

    def test_headers_vary(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member)

        #h.setVary('vary_str')
        pcs.setVaryHeader('vary_str')
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.assertEqual(d['Vary'], 'vary_str')

        h.setVary('')
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.failUnless(not d.has_key('Vary'))

    def test_headers_cache_control(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        from DateTime import DateTime
        now = DateTime()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member, time=now)

        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.failIf(d.has_key('Cache-control'))

        h.setPublic(True)  # add a token to ensure we have a cache-control header

        h.setMaxAge(30)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._getCacheControl((headers_to_add, headers_to_remove))
        self.assertEqual(d['max-age'], '30')
        d = self._parseHeaders(headers_to_add)
        texpires = rfc1123_date(now.timeTime()+30)
        self.assertEqual(d['Expires'], texpires)
        h.setMaxAge(0)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._getCacheControl((headers_to_add, headers_to_remove))
        self.assertEqual(d['max-age'], '0')
        d = self._parseHeaders(headers_to_add)
        texpires = rfc1123_date(now.timeTime()-10*365*24*3600)
        self.assertEqual(d['Expires'], texpires)
        h.setMaxAge(None)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._getCacheControl((headers_to_add, headers_to_remove))
        self.failIf(d.has_key('max_age'))
        d = self._parseHeaders(headers_to_add)
        self.failIf(d.has_key('Expires'))

        # We've removed the purgeable magic overides from
        # the code so no need to test this anymore
        # 
        ## purgeable proxy, set s-maxage
        ##pcs.setCacheConfig('squid')
        #pcs.setProxyPurgeConfig('no-rewrite')
        #self.failUnless(pcs.hasPurgeableProxy())
        #h.setSMaxAge(30)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.assertEqual(d['s-maxage'], '30')
        #h.setSMaxAge(None)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.failIf(d.has_key('s-maxage'))

        # We've removed the purgeable magic overides from
        # the code so no need to test this anymore
        # 
        ## when no purgeable proxy, don't set s-maxage
        ##pcs.setCacheConfig('zserver')
        #pcs.setProxyPurgeConfig('no-purge')
        #self.failIf(pcs.hasPurgeableProxy())
        #h.setSMaxAge(30)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.failIf(d.has_key('s-maxage'))
        #h.setSMaxAge(None)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.failIf(d.has_key('s-maxage'))

        h.setNoCache(True)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._getCacheControl((headers_to_add, headers_to_remove))
        self.assertEqual(d['no-cache'], None)
        d = self._parseHeaders(headers_to_add)
        self.assertEqual(d['Pragma'], 'no-cache')
        h.setNoCache(False)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._getCacheControl((headers_to_add, headers_to_remove))
        self.failIf(d.has_key('no-cache'))
        d = self._parseHeaders(headers_to_add)
        self.failIf(d.has_key('Pragma'))

        h.setNoStore(True)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['no-store'], None)
        h.setNoStore(False)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('no-store'))

        h.setPrivate(True) # set a new token to make sure we have the header
        h.setMaxAge(0)

        h.setPublic(True)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['public'], None)
        h.setPublic(False)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('public'))

        h.setPrivate(True)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['private'], None)
        h.setPrivate(False)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('public'))

        h.setMustRevalidate(True)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['must-revalidate'], None)
        h.setMustRevalidate(False)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('must-revalidate'))

        # We've removed the purgeable magic overides from
        # the code so no need to test this anymore
        # 
        ## purgeable proxy, set proxy-revalidate
        ##pcs.setCacheConfig('squid')
        #pcs.setProxyPurgeConfig('no-rewrite')
        #h.setProxyRevalidate(True)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.assertEqual(d['proxy-revalidate'], None)
        #h.setProxyRevalidate(False)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.failIf(d.has_key('proxy-revalidate'))

        # We've removed the purgeable magic overides from
        # the code so no need to test this anymore
        # 
        ## no purgeable proxy, don't set proxy-revalidate
        ##pcs.setCacheConfig('apache')
        #pcs.setProxyPurgeConfig('no-purge')
        #h.setProxyRevalidate(True)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.assertEqual(d.get('proxy-revalidate',None), None)
        #h.setProxyRevalidate(False)
        #d = self._getCacheControl(h.getHeaders(expr_context))
        #self.failIf(d.has_key('proxy-revalidate'))

        h.setNoTransform(True)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['no-transform'], None)
        h.setNoTransform(False)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('no-transform'))

        h.setPreCheck(5)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['pre-check'],'5')
        h.setPreCheck(None)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('pre-check'))

        h.setPostCheck(5)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.assertEqual(d['post-check'],'5')
        h.setPostCheck(None)
        d = self._getCacheControl(h.getHeaders(expr_context))
        self.failIf(d.has_key('post-check'))

    def test_headers_debug(self):
        pcs = self.portal.portal_cache_settings
        h = getattr(pcs.getHeaderSets(), 'my_hs')
        rule = getattr(pcs.getRules(), 'my_rule')
        doc = getattr(self.folder, 'doc')
        member = pcs.getMember()
        expr_context = rule._getExpressionContext(doc.REQUEST, doc, 'document_view', member)
        (headers_to_add, headers_to_remove) = h.getHeaders(expr_context)
        d = self._parseHeaders(headers_to_add)
        self.assertEqual(d['X-Caching-Rule-Id'], rule.getId())
        self.assertEqual(d['X-Header-Set-Id'], h.getId())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHeaderSet))
    suite.addTest(makeSuite(TestHeaderSetMethods))
    suite.addTest(makeSuite(TestHeaderSetOld))
    return suite
