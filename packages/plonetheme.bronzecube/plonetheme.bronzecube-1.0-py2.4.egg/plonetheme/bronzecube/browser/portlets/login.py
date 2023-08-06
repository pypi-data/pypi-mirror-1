from plone.app.portlets.portlets.login import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Renderer(BaseRenderer):
     render = ViewPageTemplateFile('login.pt')
