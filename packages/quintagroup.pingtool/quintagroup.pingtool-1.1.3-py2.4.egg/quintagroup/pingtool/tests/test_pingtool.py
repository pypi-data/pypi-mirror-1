#
# PingTool TestCase
#

from base import *

class TestPingTool(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.ptool = self.portal._getOb('portal_pingtool')
        self.portal.invokeFactory('Folder', id='f1',title='Folder 1')
        self.f1 = getattr(self.portal, 'f1', None)
        self.f1.enableSyndication()

    def testPingToolType(self):
        self.failUnless(self.ptool.meta_type==PingTool.PingTool.meta_type)

    def testGetPingProperties(self):
        obj = self.f1
        obj.getField('ping_sites').getMutator(obj)(('http://nohost/1', 'http://nohost/2'))
        obj.getField('enable_ping').getMutator(obj)(1)
        obj.getField('ping_Weblog').getMutator(obj)('http://site/url_ping_weblog')
        obj.getField('ping_RSS').getMutator(obj)('http://site/url_ping_rss')
        obj.getField('ping_RSS2').getMutator(obj)('http://site/url_ping_rss2')
        dic = self.ptool.getPingProperties(obj)
        self.failUnless(tuple(dic['ping_sites'])==('http://nohost/1','http://nohost/2'))
        self.failUnless(dic['enable_ping']==1)
        self.failUnless(dic['ping_Weblog']=='http://site/url_ping_weblog')
        self.failUnless(dic['ping_RSS']=='http://site/url_ping_rss')
        self.failUnless(dic['ping_RSS2']=='http://site/url_ping_rss2')

    def testPingFeedReader(self):
        obj = self.f1

        # test with default properties
        status, message = self.ptool.pingFeedReader(obj)
        self.failUnless(status=='failed')
        self.failUnless(message['portal_message']=='Ping is dissabled.')

        # test with customized properties
        self.ptool.invokeFactory(id = 'testsite', type_name = "PingInfo", title = 'www.TESTSITE.com (blog url)', url = 'http://pingsite')
        obj.getField('ping_sites').getMutator(obj)(('testsite',))
        obj.getField('enable_ping').getMutator(obj)(1)
        obj.getField('ping_Weblog').getMutator(obj)('http://site/url_ping_weblog')
        obj.getField('ping_RSS').getMutator(obj)('http://site/url_ping_rss')
        obj.getField('ping_RSS2').getMutator(obj)('http://site/url_ping_rss2')

        status, message = self.ptool.pingFeedReader(obj)
        self.failUnless(status=='failed')
        self.failUnless(message['portal_message']=='Ping is impossible.Setup canonical_url.')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPingTool))
    return suite
