from Products.Five.viewlet.viewlet import ViewletBase
from zope.component import getUtility, getMultiAdapter
from vice.outbound.interfaces import IFeed, IFeedSettings, IFeedConfigs
from vice.outbound.feedformats.interfaces import IFeedFormats
from zope.app.pagetemplate import ViewPageTemplateFile

class AutodiscoverFeedViewlet(ViewletBase):

    template = ViewPageTemplateFile('autodiscover.pt')

    def render(self):
        if not getUtility(IFeedSettings).enabled:
            return ''
        
        configs = IFeedConfigs(self.context, None)
        if not configs:
            return ''
            
        config = configs.configForAutodetect()
        if not config:
            return ''

        self.feed_id = config.id()
        format_info =  getUtility(IFeedFormats).getFormatInfo(config.format)
        self.feed_view = format_info['view']
        self.type = format_info['autodiscover_type']
        feed_adapter_name = format_info['feed_adapter_name']
        item_adapter_name = format_info['item_adapter_name']
        feed = getMultiAdapter((self.context, self.feed_id, item_adapter_name), 
                               IFeed, name=feed_adapter_name)
        self.title = feed.title
        return self.template()
