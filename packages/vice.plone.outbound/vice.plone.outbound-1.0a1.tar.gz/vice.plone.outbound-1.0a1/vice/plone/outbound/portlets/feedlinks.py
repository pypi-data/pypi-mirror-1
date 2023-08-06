# Zope library imports
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getUtility

# Zope2 imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMF imports
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import getExprContext, Expression

# Plone imports
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

# plone.[app.]syndication imports
from vice.outbound.interfaces import IFeedConfigs, IFeedSettings


PORTLET_TITLE = u"Syndication"
PORTLET_DESC = u"This portlet provides links to the various syndication feeds."

FORMAT_IMAGE_MAP = {'atom'  : 'atom-feed-icon',
                    'rss-2' : 'rss-feed-icon',
                    'rss-1' : 'rss-feed-icon',
                    'RSS'   : 'rss-feed-icon',
                   }


class IFeedLinksPortlet(IPortletDataProvider):
    """A portlet listing links to syndication feeds.
    """

    tal_lines = schema.List(
        title=_(u'Objects to display feeds for.'),
        description=_(u"TAL statements referring to objects to display feeds for."),
        required=True,
        value_type=schema.TextLine(),
        default=['here',])


class Assignment(base.Assignment):
    implements(IFeedLinksPortlet)

    def __init__(self, tal_lines=['here',]):
        self.tal_lines = tal_lines

    @property
    def title(self):
        return _(PORTLET_TITLE)


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('feedlinks.pt')

    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
       return getUtility(IFeedSettings).enabled

    @property
    def title(self):
        return _(PORTLET_TITLE)

    def getImageURL(self, format):
        img = FORMAT_IMAGE_MAP.get(format, 'small-feed-icon')
        return '%s/++resource++%s' % (self.context.absolute_url(), img)

    def getFeeds(self):
        all_details = []
        for obj in self._getObjects():
            try:
                cs = IFeedConfigs(obj).configs
            except TypeError:
                # Could not adapt obj, so we'll just ignore it.
                # XXX Perhaps a debug log call would be of use here?
                continue
            details = [{'name'          : c.name,
                        'format'        : c.format,
                        'id'            : c.id(),
                        'published_url' : c.published_url}
                       for c in cs if c.enabled]
            for f in details:
                if f['published_url']:
                    f['url'] = f['published_url']
                else:
                    f['url'] = '%s/%s' % (f['format'], f['id'])
                del(f['published_url'])
                del(f['id'])
            all_details.extend(details)
        return all_details

    def _getObjects(self):
        obs = []
        for tal in self.data.tal_lines:
            expr = Expression(tal)
            econtext = getExprContext(self.context.aq_inner,
                                      self.context.aq_inner
                                      )
            obs.append(expr(econtext))
        return obs


class AddForm(base.AddForm):
    form_fields = form.Fields(IFeedLinksPortlet)
    label = _(u"Add %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)

    def create(self, data):
        return Assignment(tal_lines=['here',])


class EditForm(base.EditForm):
    form_fields = form.Fields(IFeedLinksPortlet)
    label = _(u"Edit %s Portlet" % PORTLET_TITLE)
    description = _(PORTLET_DESC)
