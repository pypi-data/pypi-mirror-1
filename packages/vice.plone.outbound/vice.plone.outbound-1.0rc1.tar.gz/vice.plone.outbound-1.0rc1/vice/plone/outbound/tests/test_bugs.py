import unittest
from zope.component import adapts
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.traversing.adapters import DefaultTraversable
from vice.plone.outbound.browser.autodiscover import AutodiscoverFeedViewlet
from vice.outbound.feedformats.interfaces import IFeedFormats
from vice.outbound.interfaces import IFeed
from vice.outbound.interfaces import IFeedConfig
from vice.outbound.interfaces import IFeedConfigs
from vice.outbound.interfaces import IFeedable
from vice.outbound.interfaces import IFeedSettings

class MockFeedConfig(object):
    '''Mock IFeedConfig implementation
    '''
    implements(IFeedConfig)
    def __init__(self):
        self.format = MockFeedFormats()
 
    def id(self):
        return 'fake'

class MockFeedable(object):
    '''Mock IFeedable implementation
    '''
    implements(IFeedable, IFeedConfigs)
    def configForAutodetect(self):
        return MockFeedConfig()

class MockFeedFormats(object):
    '''Mock IFeedFormats implementation
    '''
    implements(IFeedFormats)
    def getFormatInfo(self):
        return {'view':'view', 
                'autodiscover_type':'type', 
                'item_adapter_name':'fake',
                'feed_adapter_name':'fake'}

class MockFeedSettings(object):
    '''Minimal test object to register as a IFeedSettings utility
    '''
    implements(IFeedSettings)
    enabled = True
    max_items = 0

class MockFeed(object):
    '''MockFeed, designed to provide a return from the call in viewlet.render:
        feed = getMultiAdapter((self.context, self.feed_id, item_adapter_name), 
                               IFeed, name=feed_adapter_name)
    '''
    implements(IFeed)
    adapts(IFeedable,str,str)
    title = 'fake feed'

    def __init__(self, context, feed_id, item_adapter_name):
        self.context = context
        self.feed_id = feed_id
        self.item_adapter_name = item_adapter_name

class BugTest(unittest.TestCase):
    """Tests added in the bug squashing process
    """

    def setUp(self):
        self.request = TestRequest()
        provideUtility(MockFeedSettings, IFeedSettings)
        provideUtility(MockFeedFormats, IFeedFormats)
        provideAdapter(MockFeed, name='fake')
        provideAdapter(DefaultTraversable, (None,))

    def test_issue3(self):
        """Test for http://plone.org/products/vice/issues/3
        The auto discovery HTML was including redundant <html/> tags
        """
        viewlet = AutodiscoverFeedViewlet(MockFeedable(), 
                                          self.request, None, None)
        results = viewlet.render()
        self.failUnless(MockFeed.title in results)
        self.failUnless('<html' not in results)


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(BugTest),])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
