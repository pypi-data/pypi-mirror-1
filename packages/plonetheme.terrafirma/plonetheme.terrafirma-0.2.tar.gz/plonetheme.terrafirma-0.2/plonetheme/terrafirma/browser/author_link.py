from plone.app.layout.viewlets.common import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class AuthorLinkViewlet(ViewletBase):
    render = ViewPageTemplateFile('author_link.pt')
    
    def update(self):
        super(AuthorLinkViewlet, self).update()
        

