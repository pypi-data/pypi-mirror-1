from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from vice.outbound.interfaces import IFeedSettings, IFeedConfigs
from vice.outbound.feedconfig import FeedConfig
from persistent import Persistent
from SyndicationTool import SyndicationTool
from Products.CMFCore.interfaces import ISyndicationTool
import logging


def migrate_site(site):
    def migrate_object(obj, path):
        syInfo = getattr(obj, 'syndication_information', None)
        if syInfo is None:
            return

        try:
            configs = IFeedConfigs(obj)
        except:
            logging.error('Error during outbound syndication migration - '
                          'failed to convert %s to new syndication' % path)
            # XXX TODO: Set a attribute indicated it wasn't all successful,
            # so can re-run migration again
            return
        config = FeedConfig()
        config.name = 'rss-legacy-plone'
        config.format = 'RSS'
        config.recurse = False
        config.enabled = True
        config.maxItems = syInfo.max_items
        configs.configs = ( config, )
        configs.enabled = True
        # XXX TODO: Add deprecated configs as annotations

        obj._delObject('syndication_information')

    logging.info('Outbound syndication migration started.')
    # XXX TODO: Mark migration begun

    # The following call fails because this utility has no aq context
    catalog = getToolByName(site, 'portal_catalog')
    # XXX TODO: this getsite magic is probably evil, but it's expedient
    # to get the catalog. should replace when have something better.
    # Thank hannosch for the evil. Thanks, hannosch!
    #from zope.app.component.hooks import getSite
    #site = getSite()
    catalog = getToolByName(site, 'portal_catalog')
    catalog.ZopeFindAndApply(site, apply_func=migrate_object)
    sm = site.getSiteManager()
    sm.unregisterUtility(provided=ISyndicationTool)
    site._delObject("portal_syndication")
    site._setObject("portal_syndication", SyndicationTool())
    sm.registerUtility(site["portal_syndication"].aq_base, provided=ISyndicationTool)#, name='portal_syndication')
    
    # XXX TODO: Mark migration finished
    logging.info('Outbound syndication migration finished.')
