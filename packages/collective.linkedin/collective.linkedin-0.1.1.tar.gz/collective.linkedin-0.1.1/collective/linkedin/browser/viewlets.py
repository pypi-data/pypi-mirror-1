from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, SiteActionsViewlet

from collective.linkedin.browser.config import ld_action_id
from collective.linkedin.browser.company_info import CompanyInfo

class CustomSiteActionsViewlet(SiteActionsViewlet,CompanyInfo):
    index = ViewPageTemplateFile('templates/site_actions.pt')

    def render(self):
        return self.index()

    def action_visible(self):
        settings = self.get_settings()
        return settings and settings.action_popup or None

    def show_popup(self):
        return self.company_name() and self.action_visible()

    def linkedin_action_id(self):
        return ld_action_id
