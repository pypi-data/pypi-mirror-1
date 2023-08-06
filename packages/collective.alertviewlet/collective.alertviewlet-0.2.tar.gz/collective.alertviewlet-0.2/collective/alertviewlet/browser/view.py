from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


class AlertViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/alert.pt')

    def update(self):
        properties_tool = getToolByName(self.context, 'portal_properties')
        properties = getattr(properties_tool, 'alertviewlet_properties', None)
        
        if properties is not None:
            self.message = properties.getProperty('message', None)
            self.showViewlet = properties.getProperty('showViewlet', False)
        else:
            self.message = ''
            self.showViewlet = False
        
    
