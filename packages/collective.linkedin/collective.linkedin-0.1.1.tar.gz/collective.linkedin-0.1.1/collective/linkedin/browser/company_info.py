from zope.component import getSiteManager
from collective.linkedin.browser.interfaces import ICollectiveLinkedInManagement

class CompanyInfo(object):
    def get_settings(self):
        sm = getSiteManager()
        return sm.queryUtility(ICollectiveLinkedInManagement, name='linkedin_config')

    def company_name(self):
        settings = self.get_settings()
        return settings and settings.company_insider_widget or None

