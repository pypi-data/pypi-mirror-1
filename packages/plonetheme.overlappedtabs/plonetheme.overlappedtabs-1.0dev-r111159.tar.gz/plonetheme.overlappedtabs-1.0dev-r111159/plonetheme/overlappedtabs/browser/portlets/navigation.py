from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('navigation.pt')
    recurse = ViewPageTemplateFile('navigation_recurse.pt')
