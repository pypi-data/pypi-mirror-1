import rfc822, pytz, time, DateTime
from vice.zope2.outbound.utils import RFC3339
from zope.annotation import factory
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter, getMultiAdapter, getUtility
from zope.dublincore.interfaces import IZopeDublinCore
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from Products.ATContentTypes.interface import IATFolder, IATDocument, IATEvent, \
    IATLink, IATImage, IATTopic, IATFile, IATNewsItem
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE
from zope.app.file.interfaces import IFile
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.filerepresentation.interfaces import IReadFile
from uuid import uuid1
from collective.uuid import UUIDs
from vice.outbound.interfaces import IFeed, IFeedItem, \
    IFeedConfigs, \
    IFeedConfig, IItemUUID, IItemUUIDs, IItemUUIDable, IFeedUUID, \
    IFeedUUIDable, IEnclosure, IFeedSettings
from Products.CMFCore.utils import getToolByName
import logging

class ATFeedBase(object):
    """Base class for feeds.
    """

    __name__ = __parent__ = None

    def __init__(self, context, feed_id, item_adapter_name):
        self.context = context
        self.feed_id = feed_id
        self.item_adapter_name = item_adapter_name

    def __iter__(self):
        """Iterator for all syndicated items in this feed.  This returns
        all items (ordered descending by their modified date) marked with
        the IFeedItem interface, up to the max items for the feed.
        """

        max_items = IFeedConfigs(self.context).max_items

        if self.config.recurse:
            if getUtility(IFeedSettings).recursion_enabled:
                recurse = True
            else:
                recurse = False
                logging.warn('Request for a legitimately configured recursive '
                             'feed when recursion has been disabled. Returning '
                             'non-recursive feed. Feed for: %s'
                             % str(self.context.getPhysicalPath()))
        else:
            recurse = False
            
        return self.feed_items(max_items, recurse)

    def feed_items(self, max_items=-1, recurse=False):
        if max_items is None:
            max_items = -1
        if max_items == 0:
            return

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        if recurse:
            path={'query':'/'.join(self.context.getPhysicalPath())}
        else:
            # XXX TODO: Should depth be 1?
            path={'query':'/'.join(self.context.getPhysicalPath()), 'depth':1}

        brains = portal_catalog.searchResults(path=path, sort_on='modified',)
                                              #sort_order='reverse')

        # reverse isn't working - do it by hand
        # XXX TODO: figure out why reverse isn't workign and fix
        if len(brains) == 0:
            return
        brains = reversed(brains)

        for brain in brains:
            item = queryMultiAdapter((brain.getObject(), self), IFeedItem, 
                                     name=self.item_adapter_name)
            if item is not None:
                yield item
                max_items = max_items - 1
                if max_items == 0:
                    # We'll only hit 0 if the max was set (positive) and
                    # the last one was just yielded
                    # A 'no max items' setting is a negative number to begin
                    # with, so it never hits 0 on subtraction
                    return

    @property
    def description(self):
        """See IFeed.
        """
        return self.context.description

    @property
    def modified(self):
        """See IFeed.
        """
        return self.context.modified()

    @property
    def modifiedString(self):
        return RFC3339(self.modified)

    @property
    def name(self):
        """See IFeed.
        """
        return self.context.__name__

    @property
    def title(self):
        """See IFeed.
        """
        return self.context.title

    @property
    def UID(self):
        """See IFeed.
        """
        u = IFeedUUID(self)
        return u.UUID

    @property
    def config(self):
        s = IFeedConfigs(self.context)
        return s.findConfigByID(self.feed_id)

    @property
    def alternate_url(self):
        return self.context.absolute_url()

    @property
    def self_url(self):
        return ('%s/%s/%s' 
                % (self.alternate_url, self.config.format, self.config.id())
               )

class PloneSiteRootFeed(ATFeedBase):
    """Adapter from IPloneSiteRoot to IFeed.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeed, PloneSiteRootFeed)
    True
    """

    implements(IFeed)
    adapts(IPloneSiteRoot, str, str)

class ATFolderFeed(ATFeedBase):
    """Adapter from IATFolder to IFeed.

    Make sure that ATFolderFeed implements the IFeed
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeed, ATFolderFeed)
    True
    """

    implements(IFeed)
    adapts(IATFolder, str, str)


class ATTopicFeed(ATFeedBase):
    """Adapter from IATTopic to IFeed.
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeed, ATTopicFeed)
    True
    """

    implements(IFeed)
    adapts(IATTopic, str, str)
    
    def __iter__(self):
        """ Iterate through the catalog objects, waking as needed """

        max_items = IFeedConfigs(self.context).max_items
        if max_items is None:
            max_items = -1
        if max_items == 0:
            return

        if self.config.recurse:
            if getUtility(IFeedSettings).recursion_enabled:
                recurse = True
            else:
                recurse = False
                logging.warn('Request for a legitimately configured recursive '
                             'feed when recursion has been disabled. Returning '
                             'non-recursive feed. Feed for: %s' 
                             % self.context.getPhysicalPath())
        else:
            recurse = False

        brains = list(self.context.queryCatalog(sort_on="modified"))
        
        # reverse isn't working - do it by hand
        # XXX TODO: figure out why reverse isn't working and fix
        brains.sort(lambda x,y: cmp(x.modified, y.modified))
        if len(brains) == 0:
            return
        brains = reversed(brains)

        for brain in brains:
            item = queryMultiAdapter((brain.getObject(), self), IFeedItem, name=self.item_adapter_name)
            if item is not None:
                yield item
                max_items = max_items - 1
                if max_items == 0:
                    # We'll only hit 0 if the max was set (positive) and
                    # the last one was just yielded
                    # A 'no max items' setting is a negative number to begin
                    # with, so it never hits 0 on subtraction
                    return

class ATFeedItemBase(object):
    """Base class for FeedItem classes.
    """

    def __init__(self, context, feed):
        self.context = context
        self.feed = feed

    @property
    def title(self):
        """See IFeedItem
        """
        return self.context.title

    @property
    def description(self):
        """See IFeedItem
        """
        return self.context.description

    @property
    def url(self):
        """See IFeedItem
        """
        return self.context.absolute_url()

    @property
    def relatedUrls(self):
        """See IFeedItem
        """
        return []

    @property
    def body(self):
        """See IFeedItem
        """
        return self.context.getText()

    @property
    def XHTML(self):
        """See IFeedItem
        """
        html_types = ('text/html', 'text/x-rst',
                      'text/restructured', 'text/structured')
        if self.context.text.mimetype in html_types:
            return self.context.getText()
        else:
            return None

    @property
    def UID(self):
        """See IFeedItem
        """
        u = getMultiAdapter((self.feed, self), IItemUUID)
        return u.UUID

    @property
    def author(self):
        """See IFeedItem
        """
        return self.context.creators

    @property
    def effective(self):
        """See IFeedItem
        """
        if self.context.effective() != FLOOR_DATE:
            return self.context.effective()
        elif self.context.created() != FLOOR_DATE:
            return self.context.created()
        else:
            return None

    @property
    def effectiveString(self):
        return RFC3339(self.effective)

    @property
    def modified(self):
        """See IFeedItem
        """
        mod =  self.context.modified()
        if mod == None:
            mod = self.context.effective()
        return mod

    @property
    def modifiedString(self):
        return RFC3339(self.modified)

    @property
    def tags(self):
        """See IFeedItem
        """
        return self.context.Subject()

    @property
    def rights(self):
        """See IFeedItem
        """
        return self.context.rights

    @property
    def enclosure(self):
        """See IFeedItem
        """
        return None

class ATDocumentFeedItem(ATFeedItemBase):
    """Adapter from IATDocument to IFeedItem.
    Make sure that ATDocumentFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATDocumentFeedItem)
    True
    """
    implements(IFeedItem)
    adapts(IATDocument, IFeed)
    
    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_document')
        return v().encode('utf-8')
    



class ATEventFeedItem(ATFeedItemBase):
    """Adapter from IATEvent to IFeedItem.
    Make sure that ATEventFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATEventFeedItem)
    True
    """

    implements(IFeedItem)
    adapts(IATEvent, IFeed)

    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_event')
        return v().encode('utf-8')

class ATNewsItemFeedItem(ATFeedItemBase):
    """Adapter from IATNewsItem to IFeedItem.
    Make sure that ATNewsItemFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATNewsItemFeedItem)
    True
    """

    implements(IFeedItem)
    adapts(IATNewsItem, IFeed)

    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_newsitem')
        return v().encode('utf-8')
        
class ATLinkFeedItem(ATFeedItemBase):
    """Adapter from IATLink to IFeedItem.
    Make sure that ATLinkFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATLinkFeedItem)
    True
    """

    implements(IFeedItem)
    adapts(IATLink, IFeed)

    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_link')
        return v().encode('utf-8')
        
    @property
    def url(self):
        """See IFeedItem
        """
        return self.context.getRemoteUrl()

    def relatedUrls(self):
        """See IFeedItem
        """
        return [self.context.absolute_url()]

class ATImageFeedItem(ATFeedItemBase):
    """Adapter from IATImage to IFeedItem.
    Make sure that ATImageFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATImageFeedItem)
    True
    """

    implements(IFeedItem)
    adapts(IATImage, IFeed)

    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_image')
        return v().encode('utf-8')


    @property
    def enclosure(self):
        """See IFeedItem
        """
        return IEnclosure(self.context)

class ATImageEnclosure(object):
    """ Adapter from IATImage to IEnclosure.
    Make sure that ATImageEnclosure implements the IEnclosure
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IEnclosure, ATImageEnclosure)
    True
    """

    implements(IEnclosure)
    adapts(IATImage)

    def __init__(self, context):
        self.context = context

    @property
    def mimeType(self):
        """See IEnclosure.
        """
        return self.context.getContentType()        

    @property
    def URL(self):
        """See IEnclosure.
        """
        return self.context.absolute_url()

    @property
    def size(self):
        """See IEnclosure.
        """
        return self.context.get_size()

class ATFileFeedItem(ATFeedItemBase):
    """Adapter from IATFile to IFeedItem.
    Make sure that ATImageFeedItem implements the IFeedItem
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IFeedItem, ATFileFeedItem)
    True
    """

    implements(IFeedItem)
    adapts(IATFile, IFeed)
    
    @property
    def body(self):
        """See IFeedItem
        """
        v = getMultiAdapter((self.context, self.context.REQUEST), Interface, name=u'vice_file')
        return v().encode('utf-8')


    @property
    def enclosure(self):
        """See IFeedItem
        """
        return IEnclosure(self.context)

class ATFileEnclosure(object):
    """ Adapter from IATFile to IEnclosure.
    Make sure that ATFileEnclosure implements the IEnclosure
    interface    
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IEnclosure, ATFileEnclosure)
    True
    """

    implements(IEnclosure)
    adapts(IATFile)

    def __init__(self, context):
        self.context = context

    @property
    def mimeType(self):
        """See IEnclosure.
        """
        return self.context.getContentType()        

    @property
    def URL(self):
        """See IEnclosure.
        """
        return self.context.absolute_url()

    @property
    def size(self):
        """See IEnclosure.
        """
        return self.context.get_size()
