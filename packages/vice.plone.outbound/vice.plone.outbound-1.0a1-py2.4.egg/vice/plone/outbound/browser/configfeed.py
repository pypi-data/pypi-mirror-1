from zope.component import getUtility, providedBy
from zope.publisher.browser import BrowserPage
from vice.outbound.interfaces import IFeedSettings, IFeedable

class ShowSyndicationAction(BrowserPage):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        fs =  getUtility(IFeedSettings)
        return fs.enabled and IFeedable in providedBy(self.context).flattened()
