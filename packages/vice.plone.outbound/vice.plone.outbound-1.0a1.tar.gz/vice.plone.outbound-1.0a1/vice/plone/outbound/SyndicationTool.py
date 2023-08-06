##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Vice replacement portal_syndication tool.

Provide a compatibility interface to vice.plone.outbound

$Id: SyndicationTool.py 77186 2007-06-28 19:06:19Z yuppie $

>>> from vice.plone.outbound.SyndicationTool import SyndicationTool

"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from DateTime import DateTime
from Globals import HTMLFile
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from zope.interface import implements

from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject

from Products.CMFDefault.exceptions import AccessControl_Unauthorized
from Products.CMFDefault.permissions import ManagePortal, ManageProperties

import os
from Globals import package_home

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )


from warnings import warn


from zope.component import getUtility, providedBy
from vice.outbound.interfaces import IFeedSettings, IFeedable,IFeedConfigs
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation.interfaces import IAnnotations


class SyndicationTool(UniqueObject, SimpleItem):

    """
        The syndication tool provides the interface to the vice utility for 
        syndication.
    """

    implements(ISyndicationTool)
    __implements__ = SimpleItem.__implements__

    id = 'portal_syndication'
    meta_type = 'Vice Syndication Tool'
    toolicon = '++resource++/syndication.gif'

    security = ClassSecurityInfo()

    #Default Sitewide Values
    isAllowed = 0
    syUpdatePeriod = 'daily'
    syUpdateFrequency = 1
    syUpdateBase = DateTime()
    max_items = 15

    #ZMI Methods
    manage_options = ( ( { 'label'  : 'Overview'
                         , 'action' : 'overview'
                         , 'help'   : ( 'CMFDefault'
                                      , 'Syndication-Tool_Overview.stx' )
                         }
                        ,{ 'label'  : 'Properties'
                         , 'action' : 'propertiesForm'
                         , 'help'   : ( 'CMFDefault'
                                      , 'Syndication-Tool_Properties.stx' )
                         }
                        ,{ 'label'  : 'Policies'
                         , 'action' : 'policiesForm'
                         , 'help'   : ( 'CMFDefault'
                                      , 'Syndication-Tool_Policies.stx' )
                         }
                        ,{ 'label'  : 'Reports'
                         , 'action' : 'reportForm'
                         , 'help'   : ( 'CMFDefault'
                                      , 'Syndication-Tool_Reporting.stx' )
                         }
                        )
                     )

    security.declareProtected(ManagePortal, 'overview')
    overview = HTMLFile('synOverview', _dtmldir)

    security.declareProtected(ManagePortal, 'propertiesForm')
    propertiesForm = HTMLFile('synProps', _dtmldir)

    security.declareProtected(ManagePortal, 'policiesForm')
    policiesForm = HTMLFile('synPolicies', _dtmldir)

    security.declareProtected(ManagePortal, 'reportForm')
    reportForm = HTMLFile('synReports', _dtmldir)

    security.declareProtected(ManagePortal, 'editProperties')
    def editProperties( self
                      , updatePeriod=None
                      , updateFrequency=None
                      , updateBase=None
                      , isAllowed=None
                      , max_items=None
                      , REQUEST=None
                      ):
        """
        Edit the properties for the SystemWide defaults on the
        SyndicationTool.
        """
        if isAllowed is not None:
            try:
                getUtility(IFeedSettings).enabled = bool(isAllowed)
            except:
                pass

        if updatePeriod is not None:
            self.syUpdatePeriod = updatePeriod
        else:
            try:
                del self.syUpdatePeriod
            except (AttributeError, KeyError):
                pass

        if updateFrequency is not None:
            self.syUpdateFrequency = int(updateFrequency)
        else:
            try:
                del self.syUpdateFrequency
            except (AttributeError, KeyError):
                pass

        if updateBase is not None:
            if type( updateBase ) is type( '' ):
                updateBase = DateTime( updateBase )
            self.syUpdateBase = updateBase
        else:
            try:
                del self.syUpdateBase
            except (AttributeError, KeyError):
                pass

        

        if max_items is not None:
            try:
                getUtility(IFeedSettings).max_items = int(max_items)
            except:
                pass

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect( self.absolute_url()
                                        + '/propertiesForm'
                                        + '?manage_tabs_message=Tool+Updated.'
                                        )

    security.declarePublic( 'editSyInformationProperties' )
    def editSyInformationProperties( self
                                   , obj
                                   , updatePeriod=None
                                   , updateFrequency=None
                                   , updateBase=None
                                   , max_items=None
                                   , REQUEST=None
                                   ):
        """
        Edit syndication properties for the obj being passed in.
        These are held on the syndication_information object.
        Not Sitewide Properties.
        """
        if not _checkPermission( ManageProperties, obj ):
            raise AccessControl_Unauthorized

        dAttributes = {}
        
        if updatePeriod is not None:
            dAttributes["vice.legacy.update_period"] = updatePeriod
        else:
            dAttributes["vice.legacy.update_period"] = self.syUpdatePeriod

        if updateFrequency is not None:
            dAttributes["vice.legacy.update_frequency"] = int(updateFrequency)
        else:
            dAttributes["vice.legacy.update_frequency"] = self.syUpdateFrequency

        if updateBase is not None:
            if type( updateBase ) is type( '' ):
                updateBase = DateTime( updateBase )
            dAttributes["vice.legacy.update_base"] = updateBase
        else:
            dAttributes["vice.legacy.update_base"] = self.syUpdateBase

        if max_items is not None:
            try:
                IFeedConfigs(obj).max_items = int(max_items)
            except:
                pass
        else:
            IFeedConfigs(obj).max_items = getUtility(IFeedSettings).max_items
        
        
        try:
            for tAttr in dAttributes.items():
                IAnnotations(obj)[tAttr[0]] = tAttr[1]
        except:
            raise "Syndication not enabled"

    security.declarePublic('enableSyndication')
    def enableSyndication(self, obj):
        """
        Enable syndication for the obj
        """
        warn("Use IFeedSettings.enabled or IFeedConfigs.enabled instead of portal_syndication.enabledSyndication",
                DeprecationWarning, 2)
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is Disabled'
        if obj is self:
            getUtility(IFeedSettings).enabled = True
        else:
            IFeedConfigs(obj).enabled = True
        return

        

    security.declarePublic('disableSyndication')
    def disableSyndication(self, obj):
        """
        Disable syndication for the obj; and remove it.
        """
        warn("Use IFeedSettings.enabled or IFeedConfigs.enabled instead of portal_syndication.enabledSyndication",
                DeprecationWarning, 2)
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is Disabled'
        
        if IPloneSiteRoot.implementedBy(obj):
            getUtility(IFeedSettings).enabled = False
        else:
            IFeedConfigs(obj).enabled = False
        return

    security.declarePublic('getSyndicatableContent')
    def getSyndicatableContent(self, obj):
        """
        An interface for allowing folderish items to implement an
        equivalent of PortalFolderBase.contentValues()
        """
        if hasattr(obj, 'synContentValues'):
            values = obj.synContentValues()
        else:
            values = PortalFolderBase.contentValues(obj)
        return values

    security.declarePublic('buildUpdatePeriods')
    def buildUpdatePeriods(self):
        """
        Return a list of possible update periods for the xmlns: sy
        """
        updatePeriods = ( ('hourly',  'Hourly')
                        , ('daily',   'Daily')
                        , ('weekly',  'Weekly')
                        , ('monthly', 'Monthly')
                        , ('yearly',  'Yearly')
                        )
        return updatePeriods

    security.declarePublic('isSiteSyndicationAllowed')
    def isSiteSyndicationAllowed(self):
        """
        Return sitewide syndication policy
        """
        warn("Use getUtilty(vice.outbound.interfaces.IFeedSettings).enabled instead of portal_syndication.isSiteSyndicationAllowed",
                DeprecationWarning, 2)
        return bool(getUtility(IFeedSettings).enabled)

    security.declarePublic('isSyndicationAllowed')
    def isSyndicationAllowed(self, obj=None):
        """
        Check whether syndication is enabled for the site.  This
        provides for extending the method to check for whether a
        particular obj is enabled, allowing for turning on only
        specific folders for syndication.
        """
        warn("Use IFeedSettings.enabled or IFeedConfigs.enabled instead of portal_syndication.isSyndicationAllowed",
                DeprecationWarning, 2)
        syn_tool = getUtility(ISyndicationTool)
        try:
            return ((obj and IFeedConfigs(obj).enabled) or not obj) and self.isSiteSyndicationAllowed()
        except:
            return False

    security.declarePublic('getUpdatePeriod')
    def getUpdatePeriod( self, obj=None ):
        """
        Return the update period for the RSS syn namespace.
        This is either on the object being passed or the
        portal_syndication tool (if a sitewide value or default
        is set)

        NOTE:  Need to add checks for sitewide policies!!!
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is Not Allowed'

        if obj is None:
            return self.syUpdatePeriod

        try:
            return IAnnotations(obj)["vice.legacy.update_period"]
        except:
            return 'Syndication is not Allowed'

    security.declarePublic('getUpdateFrequency')
    def getUpdateFrequency(self, obj=None):
        """
        Return the update frequency (as a positive integer) for
        the syn namespace.  This is either on the object being
        pass or the portal_syndication tool (if a sitewide value
        or default is set).

        Note:  Need to add checks for sitewide policies!!!
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'

        if obj is None:
            return self.syUpdateFrequency

        try:
            return IAnnotations(obj)["vice.legacy.update_frequency"]
        except:
            return 'Syndication is not Allowed'

    security.declarePublic('getUpdateBase')
    def getUpdateBase(self, obj=None):
        """
        Return the base date to be used with the update frequency
        and the update period to calculate a publishing schedule.

        Note:  I'm not sure what's best here, creation date, last
        modified date (of the folder being syndicated) or some
        arbitrary date.  For now, I'm going to build a updateBase
        time from zopetime and reformat it to meet the W3CDTF.
        Additionally, sitewide policy checks might have a place
        here...
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'

        if obj is None:
            when = self.syUpdateBase
            return when.ISO()

        try:
            when = IAnnotations(obj)["vice.legacy.update_base"]
            return when.ISO()
        except:
            return 'Syndication is not Allowed'

    security.declarePublic('getHTML4UpdateBase')
    def getHTML4UpdateBase(self, obj=None):
        """
        Return HTML4 formated UpdateBase DateTime
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'

        if obj is None:
            when = self.syUpdateBase
            return when.HTML4()

        try:
            when = IAnnotations(obj)["vice.legacy.update_base"]
            return when.HTML4()
        except:
            return 'Syndication is not Allowed'

    def getMaxItems(self, obj=None):
        """
        Return the max_items to be displayed in the syndication
        """
        if not self.isSiteSyndicationAllowed():
            raise 'Syndication is not Allowed'

        if obj is None:
            return getUtility(IFeedSettings).max_items

        try:
            return IFeedConfigs(obj).max_items
        except:
            return 'Syndication is not Allowed'

InitializeClass(SyndicationTool)
registerToolInterface('portal_syndication', ISyndicationTool)
