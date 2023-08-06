from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import SiteActionsViewlet as SiteActionsViewletOriginal

class SiteActionsViewlet(SiteActionsViewletOriginal):
    index = ViewPageTemplateFile('site_actions.pt')

