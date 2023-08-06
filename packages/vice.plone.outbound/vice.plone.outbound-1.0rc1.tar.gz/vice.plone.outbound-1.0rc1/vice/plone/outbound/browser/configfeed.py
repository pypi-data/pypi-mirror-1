from zope.component import getUtility, providedBy
from zope.publisher.browser import BrowserPage
from vice.outbound.interfaces import IFeedSettings, IFeedable
from Products.Five.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate import ViewPageTemplateFile

class ShowSyndicationAction(BrowserPage):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        fs =  getUtility(IFeedSettings)
        return fs.enabled and IFeedable in providedBy(self.context).flattened()

class DeactivateKssViewlet(ViewletBase):
    template = ViewPageTemplateFile('deactivate_config_kss.pt')

    def render(self):
        return self.template()
