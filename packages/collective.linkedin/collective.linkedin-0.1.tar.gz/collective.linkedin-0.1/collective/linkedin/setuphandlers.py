from zope.component import getSiteManager
from collective.linkedin.browser.interfaces import ICollectiveLinkedInManagement
from collective.linkedin.browser.config import LinkedInConfiguration
from collective.linkedin.browser.config import add_company_info_js

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('collective.linkedin_various.txt') is None:
        return

    # Add additional setup code here

    portal = context.getSite()
    add_company_info_js(portal,overwrite=True)

    sm = getSiteManager()
    if not sm.queryUtility(ICollectiveLinkedInManagement, name='linkedin_config'):
        sm.registerUtility(LinkedInConfiguration(),
                           ICollectiveLinkedInManagement,
                           'linkedin_config')
