from vice.outbound.feedformats.feedformats import DefaultFeedFormats
#from zope.component import getUtility
#from vice.outbound.feedformats.interfaces import IFeedFormats
#futil = getUtility(IFeedFormats)
DefaultFeedFormats.format_tuples.append(('RSS', 'RSS', 'vice-default', 'vice-default', 'text/xml', 'utf-8', 'application/xml+rss', False))
