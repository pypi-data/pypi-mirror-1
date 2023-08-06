from zope.component import getSiteManager
from collective.linkedin.browser.interfaces import ICollectiveLinkedInManagement

class ProfileInfo(object):
    def get_settings(self):
        sm = getSiteManager()
        return sm.queryUtility(ICollectiveLinkedInManagement, name='linkedin_config')

