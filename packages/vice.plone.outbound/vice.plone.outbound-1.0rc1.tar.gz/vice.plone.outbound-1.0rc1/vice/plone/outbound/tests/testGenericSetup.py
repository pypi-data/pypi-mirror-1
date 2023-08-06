from unittest import TestSuite, makeSuite
import zope.component.testing

from vice.outbound.interfaces import IFeed, IFeedSettings
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.PloneTestCase.PloneTestCase import PloneTestCase

from zope.component import getUtility

try:
  from Products.Five.testbrowser import Browser
except ImportError:
  from zope.testbrowser.testing import Browser



def setUp(test):
    pass

def test_suite():
    suite = TestSuite()
    #suite.addTest(makeSuite(TestBeforeInstall)) # Doesn't work due to ptc.setupPloneSite being module level
    suite.addTest(makeSuite(TestInstalled))
    suite.addTest(makeSuite(TestInstallUninstall))
    suite.addTest(makeSuite(TestForceBack))
    return suite

class TestBeforeInstall(PloneTestCase):
    
    def doIUIfNeeded(self):
        """To be overridden in the uninstalled class.  That would allow us to install then uninstall."""
        return
    
    def testNoConfiglet(self):
        self.doIUIfNeeded()
        configlets = self.portal.portal_controlpanel._actions
        self.assertFalse("syndication" in [a.id for a in configlets])
    
    def testProductAvailable(self):
        self.doIUIfNeeded()
        self.assertTrue(self.portal.portal_quickinstaller.isProductAvailable("vice.plone.outbound"))
    
    def testProductInstallable(self):
        self.doIUIfNeeded()
        self.assertTrue(self.portal.portal_quickinstaller.isProductInstallable("vice.plone.outbound"))
    
    def testProductNotInstalled(self):
        self.doIUIfNeeded()
        self.assertFalse(self.portal.portal_quickinstaller.isProductInstalled("vice.plone.outbound"))
    
    def testNoSettingsUtility(self):
        from zope.component.interfaces import ComponentLookupError
        self.doIUIfNeeded()
        try:
            getUtility(IFeedSettings)
        except ComponentLookupError:
            pass
        else:
            self.fail()
    
    def testNoCSS(self):
        self.doIUIfNeeded()
        self.assertFalse('++resource++vice.css' in self.portal.portal_css.getResourceIds())

class TestInstalled(TestBeforeInstall):

    def doIUIfNeeded(self):
        """To be overridden in the uninstalled class.  That would allow us to install then uninstall."""
        self.portal.portal_quickinstaller.installProduct("vice.plone.outbound")
        return

    def testNoConfiglet(self):
        self.doIUIfNeeded()
        configlets = self.portal.portal_controlpanel._actions
        self.assertTrue("syndication" in [a.id for a in configlets])


    def testProductAvailable(self):
        self.doIUIfNeeded()
        self.assertTrue(self.portal.portal_quickinstaller.isProductAvailable("vice.plone.outbound"))

    def testProductInstallable(self):
        self.doIUIfNeeded()
        self.assertTrue(self.portal.portal_quickinstaller.isProductInstallable("vice.plone.outbound"))

    def testProductNotInstalled(self):
        self.doIUIfNeeded()
        self.assertTrue(self.portal.portal_quickinstaller.isProductInstalled("vice.plone.outbound"))

    def testNoSettingsUtility(self):
        from zope.component.interfaces import ComponentLookupError
        self.doIUIfNeeded()
        try:
            getUtility(IFeedSettings)
        except ComponentLookupError:
            self.fail()
        else:
            pass

    def testNoCSS(self):
        self.doIUIfNeeded()
        self.assertTrue('++resource++vice.css' in self.portal.portal_css.getResourceIds())
    
class TestInstallUninstall(TestBeforeInstall):
    
    def doIUIfNeeded(self):
        if self.portal.portal_quickinstaller.isProductInstalled("vice.plone.outbound"):
            self.portal.portal_setup.runAllImportStepsFromProfile('profile-vice.plone.outbound:uninstall')
            self.portal.portal_quickinstaller.uninstallProducts(("vice.plone.outbound",))

class TestForceBack(PloneTestCase):
    def testPutViceBack(self):
        self.portal.portal_quickinstaller.installProducts(("vice.plone.outbound",))
