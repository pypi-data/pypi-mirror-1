from plone.app.portlets.portlets.news import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('news.pt')