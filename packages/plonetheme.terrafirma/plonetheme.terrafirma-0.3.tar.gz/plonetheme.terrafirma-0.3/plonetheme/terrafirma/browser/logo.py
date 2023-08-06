from plone.app.layout.viewlets.common import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class LogoViewlet(ViewletBase):
    render = ViewPageTemplateFile('logo.pt')
    
    def update(self):
        super(LogoViewlet, self).update()
        
        self.navigation_root_url = self.portal_state.navigation_root_url()
        
        portal = self.portal_state.portal()
        logoName = portal.restrictedTraverse('base_properties').logoName
        self.logo_tag = portal.restrictedTraverse(logoName).tag()
        
        self.portal_title = self.portal_state.portal_title()

