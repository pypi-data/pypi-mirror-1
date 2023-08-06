from vice.plone.outbound.config import GLOBALS
from vice.outbound.interfaces import IFeedConfigs
from vice.outbound.tests.basefunctional \
    import BaseTestFeeds, ITestSyndicated, getDataDir, \
           ITestSyndicatedWithEnclosure, EntryChecker, FeedChecker
from vice.outbound.feedconfig import FeedConfig
from zope.interface import implements, Interface, providedBy, alsoProvides
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from Products.Five.testbrowser import Browser
import time
import os
from Products.Five import zcml
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.ATContentTypes.interface import IATDocument, IATEvent, IATNewsItem
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE
# I shouldn't be using this to validate feed correctness, as it's used in
# producing the feed and thus can't check itself, but I couldn't find another
# good way to compare the dates without incurring timezone/DST issues
from vice.zope2.outbound.utils import RFC3339
from vice.zope2.outbound.utils import DT2dt

from Products.PloneTestCase.PloneTestCase import setupPloneSite
setupPloneSite()

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
    type_criterion = new_topic.addCriterion('Type', 'ATPortalTypeCriterion' )
    type_criterion.setValue("Document")
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

class TestMigration(FunctionalTestCase):
    def testMigration(self):
        self.createData()

        browser = Browser()
        self.browser = browser

        # XXX TODO: re-enable once know how to do layers to isolate pure-3.0
        # from 3.0+Vice - currently, it's picking up the Vice packages
        # before migration has run and /RSS fails because it tries to use
        # the Vice view rather than the legacy stuff
#        self.oldFeedsTest()
        self.migrate()
        self.oldFeedsTest()
        self.newFeedsTest()
        self.synToolTest()

    def synToolTest(self):
        s_tool = getToolByName(self.portal, 'portal_syndication')
        self.assertTrue(s_tool.isSiteSyndicationAllowed())
        self.assertEquals(s_tool.getUpdatePeriod(), 'daily')
        self.assertEquals(s_tool.getUpdateFrequency(), 1)
        
        self.assertTrue(not s_tool.isSyndicationAllowed(self.portal))
        s_tool.editProperties(isAllowed=False)
        try:
            s_tool.enableSyndication(self.portal)
        except:
            pass
        else:
            self.fail('No exception')

        try:
            self.assertRaises('Syndication is Disabled', s_tool.disableSyndication)
        except:
            pass
        else:
            self.fail('No exception')

        try:
            self.assertRaises('Syndication is not Allowed', s_tool.getUpdateBase)
        except:
            pass
        else:
            self.fail('No exception')

        try:
            self.assertRaises('Syndication is not Allowed', s_tool.getUpdateHTML4Base)
        except:
            pass
        else:
            self.fail('No exception')

        try:
            self.assertRaises('Syndication is not Allowed', s_tool.getUpdatePeriod)
        except:
            pass
        else:
            self.fail('No exception')

        try:
            self.assertRaises('Syndication is not Allowed', s_tool.getUpdateFrequency)
        except:
            pass
        else:
            self.fail('No exception')

        s_tool.editProperties(isAllowed=True)
        s_tool.enableSyndication(self.portal)
        self.assertTrue(s_tool.isSyndicationAllowed(self.portal))
        s_tool.disableSyndication(self.portal)
        self.assertTrue(not s_tool.isSyndicationAllowed(self.portal))
        s_tool.enableSyndication(self.portal)
        
        self.assertTrue(s_tool.getSyndicatableContent(self.portal) is not None)
        
        self.assertTrue(s_tool.getUpdateBase() is not None)
        self.assertTrue(s_tool.getUpdateBase(self.portal) is not None)
        self.assertTrue(s_tool.getHTML4UpdateBase() is not None)
        self.assertTrue(s_tool.getHTML4UpdateBase(self.portal) is not None)
        
        self.assertEqual(s_tool.getMaxItems(), -1)
        self.assertEqual(s_tool.getMaxItems(self.portal), -1)
        
    def createData(self):
        self.setRoles(['Manager'])
        content_name = 'twodocdir-legacy'
        feed = _dir(self.portal, content_name,
                    description=u'Two file directory')
        feed = _doc(feed, u'file1', u'data would be here', u'text/plain')
        time.sleep(2) # two entries with same timestamp is invalid
        feed = _doc(feed, u'file2', u'more data would be here', u'text/plain')
        self.feed = feed

        feed.portal_syndication.enabled = True
        feed.portal_actions.object.syndication.visible = True
        adminBrowser = Browser()
        adminBrowser.open(self._getRoot().absolute_url())
        adminBrowser.getControl('Log in').click()
        adminBrowser.getControl('Login Name').value = 'manager'
        adminBrowser.getControl('Password').value = 'secret'
        adminBrowser.getControl('Log in').click()
        adminBrowser.open(self.feed.absolute_url() + '/synPropertiesForm')
        adminBrowser.getControl('Enable Syndication').click()
        adminBrowser.getControl('Save').click()
        self.adminBrowser = adminBrowser

    def oldFeedsTest(self):
        self.browser.handleErrors = False
        self.browser.open(self.feed.absolute_url() + '/RSS')
        # will get 404 if test fails

    def migrate(self):
        zcml.load_site()        
        adminBrowser = self.adminBrowser
        adminBrowser.open(self._getRoot().absolute_url() + '/portal_setup/manage_importSteps')
#        adminBrowser.getControl('Import').click()
        adminBrowser.getControl(name='context_id', index=0).displayValue = ('Outbound Syndication (Vice)',)
        adminBrowser.getControl(name='context_id', index=1).value = 'profile-vice.plone.outbound:default'
        adminBrowser.getControl('Import all steps').click()
        time.sleep(5)
        adminBrowser.open(self._getRoot().absolute_url() + '/syndication-controlpanel')
        adminBrowser.getControl('Enabled').selected = True
        adminBrowser.getControl('Show feed configuration actions').selected = True
        adminBrowser.getControl('Save').click()
        adminBrowser.getControl('Migrate').click()

    def newFeedsTest(self):
        self.browser.handleErrors = False
        self.browser.open(self.feed.absolute_url() + '/@@rss-1/rss-legacy-plone')
        # will get 404 if test fails

    def _getRoot(self):
        return self.portal

    def afterSetUp(self):
        #zcml.load_site()
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('manager', 'secret', ('Manager',), ())

def test_suite():
    from unittest import TestSuite, makeSuite
    return makeSuite(TestMigration)
    return suite
