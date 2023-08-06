from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope import schema
from zope.formlib.form import FormFields
from zope.schema import ValidationError

from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode


class IAlertSchema(Interface):
    
    message = schema.Text(
        title=_(u'Message'),
        description=_(u"Alert to display (html is allowed)"),
        required=True)
    
    showViewlet = schema.Bool(
        title=_(u'Enable'),
        description=_(u"Make the message visible sitewide "),
        default=True)
    


class AlertControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IAlertSchema)
     
    def __init__(self, context):
        super(AlertControlPanelAdapter, self).__init__(context)
        self.portal = context
        self.pprop = getToolByName(self.portal, 'portal_properties').alertviewlet_properties
        if not self.pprop.hasProperty('message'):
            self.pprop._setProperty('message','Alert','string')
        if not self.pprop.hasProperty('showViewlet'):
            self.pprop._setProperty('showViewlet','False','boolean')
    
    def get_message(self):
       message = getattr(self.pprop, 'message', u'')
       return safe_unicode(message)
    
    def set_message(self, message):
       self.pprop._updateProperty('message',message)
    
    def get_showViewlet(self):
       showViewlet = getattr(self.pprop, 'showViewlet', u'')
       return safe_unicode(showViewlet)
    
    def set_showViewlet(self, showViewlet):
       self.pprop.showViewlet = showViewlet
       self.pprop._updateProperty('showViewlet',showViewlet)
    
    message = property(get_message, set_message)
    showViewlet = property(get_showViewlet, set_showViewlet)


class AlertControlPanel(ControlPanelForm):
     
    form_fields = FormFields(IAlertSchema)
    label = _("Alert message settings")
    description = _("Alert message settings for this site.")
    form_name = _("Alert message settings")
