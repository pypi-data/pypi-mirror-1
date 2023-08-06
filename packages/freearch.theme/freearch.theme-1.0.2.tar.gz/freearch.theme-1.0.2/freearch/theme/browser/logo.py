from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class LogoViewlet(ViewletBase):
    """ Render site logo. 
    
    Override viewlet to use our custom template. 
    """
    render = ViewPageTemplateFile('templates/logo.pt')

    def update(self):
        super(LogoViewlet, self).update()
        self.navigation_root_url = self.portal_state.navigation_root_url()

