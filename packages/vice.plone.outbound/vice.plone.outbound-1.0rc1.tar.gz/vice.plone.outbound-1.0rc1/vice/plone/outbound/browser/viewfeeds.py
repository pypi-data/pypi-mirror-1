from zope.publisher.browser import BrowserPage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from vice.outbound.interfaces import IFeedConfigs, IFeedSettings
from vice.outbound.feedformats.interfaces import IFeedFormats
from zope.component import getUtility
import logging

class ViewFeeds(ViewletBase):
    """Browser view for feed links to be shown in a document
    actions viewlet in Plone.
    """
    
    render = ViewPageTemplateFile('view_feeds.pt')
    def feeds(self):
       settings = getUtility(IFeedSettings)
       if not settings.enabled:
           return []
       cs = IFeedConfigs(self.context).configs
       stuff = [{'name':c.name, 'format_view':c.format, 'id':c.id(),
                 'published_url':c.published_url, 
                 'enabled':c.enabled} 
                for c in cs]
       for f in stuff:
           if f['published_url']:
               if settings.published_url_enabled:
                   f['url'] = f['published_url']
               else:
                   f['url'] = default_url(f['format_view'], f['id'])
                   logging.warn('Different published URL requested but '
                               'published URLs are disabled. Returning %s'
                               % f['url'])
           else:
               f['url'] = default_url(f['format_view'], f['id'])
           del(f['published_url'])
           del(f['format_view'])
           del(f['id'])
       return stuff

def default_url(format_view, id):
       return '%s/%s' % (format_view,id)
