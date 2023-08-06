from zope.interface import implements
from zope.component import adapts, getUtility
from zope.interface import Interface, Attribute
from zope.formlib import form
from zope.formlib.form import FormFields
from zope.schema import Bool, Choice, Datetime, Field, Iterable, List, \
    Object, Text, TextLine, Tuple, URI, Dict
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFCore.utils import getToolByName
from plone.app.form.validators import null_validator
from plone.fieldsets.form import FieldsetsEditForm
from plone.app.controlpanel.interfaces import IPloneControlPanelForm
from vice.outbound.interfaces import IFeedSettings
from rwproperty import getproperty, setproperty
from zope.i18nmessageid import MessageFactory

import migrate

_ = MessageFactory('vice')

class IFeedSettingsConfigletSchema(IFeedSettings):

    showConfigsOnContainers = Bool(title=_(u'Show feed configuration actions'),
                                   description=(u'Display option to configure '
                                                u'feeds on all containers (to '
                                                u'users with correct role).'),
                                   default=False)

class FeedSettingsAdapter(object):

    implements(IFeedSettingsConfigletSchema)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.feedsettings = getUtility(IFeedSettings)
        self.portalactions = getToolByName(context, 'portal_actions')

    @getproperty
    def enabled(self):
        return self.feedsettings.enabled

    @setproperty
    def enabled(self, enabled):
       self.feedsettings.enabled = enabled

    @getproperty
    def showConfigsOnContainers(self):
        return self.portalactions.object.syndication.visible

    @setproperty
    def showConfigsOnContainers(self, visible):
        self.portalactions.object.syndication.visible = visible

    @getproperty
    def max_items(self):
        return self.feedsettings.max_items

    @setproperty
    def max_items(self, max_items):
        self.feedsettings.max_items = max_items

    @getproperty
    def published_url_enabled(self):
        return self.feedsettings.published_url_enabled

    @setproperty
    def published_url_enabled(self, published_url_enabled):
        self.feedsettings.published_url_enabled = published_url_enabled

    @getproperty
    def recursion_enabled(self):
        return self.feedsettings.recursion_enabled

    @setproperty
    def recursion_enabled(self, recursion_enabled):
        self.feedsettings.recursion_enabled = recursion_enabled

class FeedSettingsControlPanel(FieldsetsEditForm):

    implements(IPloneControlPanelForm)

    form_fields = FormFields(IFeedSettingsConfigletSchema)

    label = _("Syndication Settings")
    description = _("Syndication settings for this site.")
    form_name = _("Syndication settings")

    # XXX TODO: Don't display if migration already successfully run once
    # with no errors
    @form.action(_(u'Migrate'))
    def handle_migrate_action(self, action, data):
        migrate.migrate_site(self.context)

    @form.action(_(u'Save'))
    def handle_edit_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'Cancel'), validator=null_validator)
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
        
    def _on_save(self, data=None):
        pass
