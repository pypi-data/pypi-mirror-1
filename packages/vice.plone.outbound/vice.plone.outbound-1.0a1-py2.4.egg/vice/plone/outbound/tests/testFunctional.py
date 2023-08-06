from vice.plone.outbound.config import GLOBALS
from vice.outbound.interfaces import IFeedConfigs
from vice.outbound.tests.basefunctional \
    import BaseTestFeeds, ITestSyndicated, getDataDir, \
           ITestSyndicatedWithEnclosure, EntryChecker, FeedChecker
from vice.outbound.feedconfig import FeedConfig
from zope.interface import implements, Interface, providedBy, alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from vice.outbound.interfaces import IFeedConfigs
from vice.outbound.feedconfig import FeedConfig
from vice.outbound.interfaces import IFeed, IFeedItem, \
    IFeedSettings
import time
import os
import warnings
import DateTime
from Products.Five import zcml
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.ATContentTypes.interface import IATDocument, IATEvent, IATNewsItem, IATTopic
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE
# I shouldn't be using this to validate feed correctness, as it's used in
# producing the feed and thus can't check itself, but I couldn't find another
# good way to compare the dates without incurring timezone/DST issues
from vice.zope2.outbound.utils import RFC3339
from vice.zope2.outbound.utils import DT2dt
from Products.PloneTestCase.PloneTestCase import setupPloneSite
setupPloneSite(extension_profiles=('vice.plone.outbound:default',))

def _publish(item):
    item.content_status_modify(workflow_action='publish')
#    wftool = getToolByName(item, 'portal_workflow')
#    wftool.notifyCreated(item)
#    if not wftool.getTransitionsFor(item):
#       return
#    wftool.doActionFor(item, 'publish')

def _dir(location, name, **kwargs):
    """Build a directory

    location The parent location
    format The format for the feed on this directory
    name The name of the new directory

    **kwargs
    title The dc title of the new directory
    description The dc description of the new directory

    Returns the new directory
    """

    title = kwargs.get('title',name)
    location.invokeFactory('Folder', id=name, title=title)
    new_folder = location[name]
    _publish(new_folder)
    return new_folder

def _doc(folder, name, type, data, **kwargs):
    """ Add an ATDocument to the folder as a syndicated item """
    title = kwargs.get('title',name)
    folder.invokeFactory('Document', id=name, title=title)
    _publish(folder[name])
    alsoProvides(folder[name], ITestSyndicated)
    return folder

def _topic(location, name, **kwargs):
    title = kwargs.get('title',name)
    location.invokeFactory('Topic', id=name, title=title)
    new_topic = location[name]
    type_criterion = new_topic.addCriterion('portal_type', 'ATPortalTypeCriterion' )
    type_criterion.update(**{"value":["Document"]})
    _publish(new_topic)
    return new_topic

def _event(folder, name, **kwargs):
    title = kwargs.get('title',name)
    folder.invokeFactory('Event', id=name, title=title)
    event = folder[name]
    event.location = kwargs.get('location','')
    event.setContactName(kwargs.get('contactName',''))
    event.setContactPhone(kwargs.get('contactPhone',''))
    _publish(event)
    alsoProvides(event, ITestSyndicated)
    return folder

def _link(folder, name, **kwargs):
    title = kwargs.get('title', name)
    folder.invokeFactory('Link', id=name, title=title)
    link = folder[name]
    link.setRemoteUrl(kwargs.get('remoteUrl',''))
    _publish(link)
    alsoProvides(link, ITestSyndicated)
    return folder

def _file(folder, name, type='', data='', **kwargs):
    title = kwargs.get('title',name)
    folder.invokeFactory('File', id=name, title=title)
    _publish(folder[name])
    alsoProvides(folder[name], ITestSyndicatedWithEnclosure)
    return folder

def _image(folder, name):
    """ Create an ATImage by the same name as the file name passed in, and add
    it to the provided folder - marking as syndicated
    """
    img = open(os.path.join(getDataDir(GLOBALS), name))
    folder.invokeFactory('Image', id=name)
    image = folder[name]
    image.setImage(img)
    _publish(image)
    alsoProvides(image, ITestSyndicatedWithEnclosure)
    return image

def _newsitem(folder, name, **kwargs):
    title = kwargs.get('title',name)
    folder.invokeFactory('News Item', id=name, title=title)
    ni = folder[name]
    ni.setText(kwargs.get('text', u''))
    ni.setImageCaption(kwargs.get('caption', u''))
    _publish(ni)
    alsoProvides(ni, ITestSyndicated)
    return folder

# Each of the following functions sets up a directory (and makes it
# syndicatable) and adds items to be syndicated to it.


def createTestEmptyDir(root, format):
    content_name = 'emptydir-%s' % format
    feed = _dir(root, content_name, 
                description=u'Empty directory')
    return (content_name, feed)

def createTestOneDocDir(root, format):
    content_name = 'onedocdir-%s' % format
    feed = _dir(root, content_name,
                description=u'One file directory')
    feed = _doc(feed, u'file1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    return (content_name, feed)

def createTestTwoDocDir(root, format):
    content_name = 'twodocdir-%s' % format
    feed = _dir(root, content_name,
                description=u'Two file directory')
    feed = _doc(feed, u'file1', u'data would be here', u'text/plain')
    time.sleep(2) # two entries with same timestamp is invalid
    feed = _doc(feed, u'file2', u'more data would be here', u'text/plain')
    return (content_name, feed)

def createTestEventDir(root, format):
    content_name = 'eventdir-%s' % format
    feed = _dir(root, content_name,
                description=u'Event directory')
    feed = _event(feed, u'event1', location='Boston, MA', contactName='Homer Simpson', contactPhone='617-555-1212')
    return (content_name, feed)

def createTestLinkDir(root, format):
    content_name = 'linkdir-%s' % format
    feed = _dir(root, content_name,
                description=u'Link directory')
    feed = _link(feed, u'link1', remoteUrl=u'http://www.plone.org')
    return (content_name, feed)

def createTestImageDir(root, format):
    content_name = 'imagedir-%s' % format
    feed = _dir(root, content_name,
               description=u'Images directory')
    image = _image(feed, "thumbnail.jpg")
    return (content_name, feed)

def createTestFileDir(root, format):
    content_name = 'filedir-%s' % format
    feed = _dir(root, content_name,
               description=u'Files directory')
    image = _file(feed, "empty.txt")
    return (content_name, feed)

def createTestTopic(root, format):
    content_name = 'topic-%s' % format
    feed = _topic(root, content_name)
    return (content_name, feed)

def createTestNewsItem(root, format):
    content_name = 'newsitemdir-%s' % format
    feed = _dir(root, content_name,
               description=u'NewsItem directory')
    feed = _newsitem(feed, 'some news', caption='an image goes above', text='<b>BOO!</b>')
    return (content_name, feed)

def createBigDir(root, format):
    content_name = 'bigdir-%s' % format
    feed = _dir(root, content_name,
               description=u'All content types directory')
    _doc(feed, u'file1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    _event(feed, u'event1', location='Boston, MA', contactName='Homer Simpson', contactPhone='617-555-1212')
    _link(feed, u'link1', remoteUrl=u'http://www.plone.org')
    _image(feed, "thumbnail.jpg")
    _file(feed, "empty.txt")
    _newsitem(feed, 'some news', caption='an image goes above', text='<b>BOO!</b>')
    return (content_name, feed)
    
def createRecursiveFeed(root, format):
    content_name = 'recursivedir-%s' % format
    feed = _dir(root, content_name,
                description=u'Nested directories')
    feed = _doc(feed, u'file1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    subdir = _dir(feed, 'nesteddir', description='The nested')
    _doc(subdir, u'filenested', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    return (content_name, feed)

def createRecursiveFourDocFeed(root, format):
    content_name = 'recursiveExceedingMax-%s' % format
    feed = _dir(root, content_name,
                description=u'Recursive exceeding max items')
    configs = IFeedConfigs(feed)
    configs.max_items = 3
    feed = _doc(feed, u'addorder-0', u'text/plain', u'This should be the first modified.', description=u'A description for this file.')
    subdir = _dir(feed, 'nesteddir', description='The nested')
    time.sleep(2) # two entries with same timestamp is invalid
    _doc(subdir, u'addorder-1', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    time.sleep(2) # two entries with same timestamp is invalid
    _doc(feed, u'addorder-2', u'text/plain', u'Blah.', description=u'A description for this file.')
    _doc(subdir, u'addorder-3', u'text/plain', u'Data would be here.', description=u'A description for this file.')
    _doc(feed, u'addorder-4', u'text/plain', u'This should be the last modified.', description=u'A description for this file.')
    return (content_name, feed)

class TestPloneFeeds(BaseTestFeeds, FunctionalTestCase):
    def _getRoot(self):
        return self.portal

    def getTestFactories(self):
        return (createTestEmptyDir, 
                createBigDir,
                createTestTopic,
                createRecursiveFeed,
                createRecursiveFourDocFeed,
               )

    def getSyndicatableItems(self, container, ifd, recurse, test):
        """Return a dictionary whose values are all the items in the container
        that are syndicatable (i.e. adaptable to IFeedItem).  The keys are
        the urls used in the feeds.
        """
        syndItems = {}
        values = container.values()
        subobjects = values[:]
        if IATTopic.providedBy(container):
            values = container.queryCatalog()
            values = [v.getObject() for v in values]
        for item in values:
            ifaces = providedBy(item).flattened()
            if ITestSyndicated in ifaces:
                if queryMultiAdapter((item, ifd), IFeedItem, name=ifd.item_adapter_name):
                    syndItems[self.getLinkForItem(item)] = item
                else:
                    test.fail("""'%s' marked ITestSyndicated w/o an IFeedItem 
                              adapter""" % item.__class__)
            else:
                if queryMultiAdapter((item, ifd), IFeedItem, name=ifd.item_adapter_name):
                    test.fail("""'%s' incorrectly not marked ITestSyndicated""" % item)
        for item in subobjects:
            if recurse and isFolderish(item):
                for a in self.getSyndicatableItems(item, ifd, recurse, test).items():
                    syndItems[a[0]] = a[1]
        return syndItems


    def feed(self, feedable, name, format, recurse, enabled, max_items=-1):
        self.adminBrowser.open(feedable.absolute_url() + '/configurefeeds')
        self.adminBrowser.getControl('Enable syndication').selected = enabled
        self.adminBrowser.getControl('Maximum Items').value = unicode(max_items)
        self.adminBrowser.getControl('Add Feeds').click()
        self.adminBrowser.getControl(name='form.configs.0.name').value = name
        self.adminBrowser.getControl(name='form.configs.0.format').displayValue = [self.decodeFormat(format)]
        self.adminBrowser.getControl(name='form.configs.0.recurse').value = recurse
        self.adminBrowser.getControl(name='form.configs.0.enabled').value = enabled
        self.adminBrowser.getControl('Apply').click()
#        configs = IFeedConfigs(feedable)
#        config = FeedConfig()
#        config.name = name
#        config.format = format
#        config.recurse = recurse
#        config.enabled = enabled
#        config.max_items = max_items
#        configs.configs = ( config, )
#        configs.enabled = enabled
#        return feedable

    def createFeedChecker(self, fed, ifd, feed, format):
        return PloneFeedChecker(fed, ifd, feed, self, format)

    def createEntryChecker(self, eo, entry, ifd, format):
        return PloneEntryChecker(eo, entry, ifd, self, format)

    def getLinkForItem(self, item):
        if isinstance(item, ATLink):
            return item.getRemoteUrl()
        else:
            return item.absolute_url()

    def afterSetUp(self):
        zcml.load_site()
        super(TestPloneFeeds, self).afterSetUp()
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('manager', 'secret', ('Manager',), ())
        alsoProvides(self.portal['front-page'], ITestSyndicated)

    def global_setup(self, enabled, visible, max_items, published_url_enabled,
                     recursion_enabled):
        self.adminBrowser.open('%s/syndication-controlpanel' \
                               % self._getRoot().absolute_url())
        self.adminBrowser.getControl('Enabled').selected = enabled
        self.adminBrowser.getControl('Show feed configuration actions').selected = visible
        self.adminBrowser.getControl('Maximum Items').value = unicode(max_items)
        self.adminBrowser.getControl('Enable Published URLs').selected = published_url_enabled
        self.adminBrowser.getControl('Enable Recursion').selected = recursion_enabled
        self.adminBrowser.getControl('Save').click()

class PloneFeedChecker(FeedChecker):
    def modified(self):
        if self.obj.modified():
            self.test.assertEqual(self.feed.updated_parsed, DT2dt(self.obj.modified()).utctimetuple())
        else:
            self.test.assertEqual(self.feed.updated_parsed, self.obj.created().utctimetuple())


class PloneEntryChecker(EntryChecker):
    def created(self):
        # We shouldn't be using RFC3339 to validate feed correctness, as
        # it's used in producing the feed and thus can't check itself,
        # but given the timezone/DST issues, we know no other option.
        myZone = DateTime.DateTime().timezone()
        if self.obj.effective() != FLOOR_DATE:
            self.test.assertEquals(self.entry.published, 
                                   RFC3339(self.obj.effective()))
        elif self.obj.created() != FLOOR_DATE:
            self.test.assertEquals(self.entry.published, 
                                   RFC3339(self.obj.created()))
        else:
            self.test.assertEquals(self.entry.published, '')

    def modified(self):
        # We shouldn't be using RFC3339 to validate feed correctness, as
        # it's used in producing the feed and thus can't check itself,
        # but given the timezone/DST issues, we know no other option.
        if self.obj.modified():
            self.test.assertEquals(self.entry.updated, RFC3339(self.obj.modified()))
        else:
            self.test.assertEquals(self.entry.updated, RFC3339(self.obj.effective()))

    def content(self):
        content = self.entry.content[0].value
        ifaces = providedBy(self.obj).flattened()
        if IATEvent in ifaces:
            self.test.failUnless(unicode(self.obj.location) in content)
            self.test.failUnless(unicode(self.obj.contact_name()) in content)
            self.test.failUnless(unicode(self.obj.contact_phone()) in content)
        elif IATNewsItem in ifaces:
            self.test.failunless(unicode(self.obj.getImageCaption()) in content)
            self.test.failunless(unicode(self.obj.absoluate_url()) in content)
            self.test.failunless(unicode(self.obj.getText()) in content)
        elif IATDocument in ifaces:
            self.test.assertEquals(content, self.obj.getText())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneFeeds))
    return suite


try:
    # From Plone 2.1
    from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
except ImportError, e:
    # Up to Plone 2.0.5
    INonStructuralFolder = None
from Acquisition import aq_base

def isFolderish(content):
    """Can we walk in this content (recursively) ?"""
    if IATTopic.providedBy(content):
        return False
    if INonStructuralFolder is not None:
        # Plone 2.1 and up
        if INonStructuralFolder.isImplementedBy(content):
            return False
    return bool(getattr(aq_base(content), 'isPrincipiaFolderish', False))

