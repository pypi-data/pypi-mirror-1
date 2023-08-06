from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class SteelerBanner(ViewletBase):
    index = ViewPageTemplateFile('viewlet.pt')