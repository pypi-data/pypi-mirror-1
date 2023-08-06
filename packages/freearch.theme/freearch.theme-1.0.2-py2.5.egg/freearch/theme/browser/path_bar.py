from plone.app.layout.viewlets.common import PathBarViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FreeArchPathBarViewlet(PathBarViewlet):
    render = ViewPageTemplateFile('templates/path_bar.pt')

