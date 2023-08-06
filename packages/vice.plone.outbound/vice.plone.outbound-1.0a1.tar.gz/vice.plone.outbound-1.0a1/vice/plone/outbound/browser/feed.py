from zope.publisher.browser import BrowserPage
from zope.formlib.namedtemplate import NamedTemplate
from zope.component import provideAdapter
from vice.outbound.browser.feed import FeedViewBase
from vice.outbound.browser import legacy_rss

class PloneCompatibilityRSS_1_0_FeedView(FeedViewBase):
    """Browser view for RSS 1.0 feeds that are backwards compatible
    with pre-version 3.5 Plone. This is NOT the right way to do
    things going forward!
    """

    def __init__(self, context, request):
        self.feed_name = 'rss-legacy-plone'
        super(BrowserPage, self).__init__(context, request)

    template = NamedTemplate('RSS')

    def getTemplate(self):
        return self.template

provideAdapter(legacy_rss, 
               [PloneCompatibilityRSS_1_0_FeedView],
               name='RSS')
