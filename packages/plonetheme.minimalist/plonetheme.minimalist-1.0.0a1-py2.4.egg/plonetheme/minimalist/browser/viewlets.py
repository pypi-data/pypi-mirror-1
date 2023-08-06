from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from plone.app.layout.viewlets import common 


class SiteActionsViewlet(common.SiteActionsViewlet):
    """siteaction customizado"""
    render = ViewPageTemplateFile('templates/site_actions.pt')
 

