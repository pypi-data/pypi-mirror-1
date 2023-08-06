from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm

from collective.linkedin.browser.interfaces import ICollectiveLinkedInManagement
from collective.linkedin import LinkedInMessageFactory as _


ld_action_id = 'linkedin_company_info'
ci_url = "http://www.linkedin.com/companyInsider?script&useBorder=%s"

def add_company_info_js(portal,border=True,overwrite=False):
    pjs = portal.portal_javascripts

    if border:
        old_url = ci_url % "no"
        new_url = ci_url % "yes"
    else:
        old_url = ci_url % "yes"
        new_url = ci_url % "no"

    if overwrite:
        if pjs.getResource(old_url) is not None:
            pjs.manage_removeScript(id=old_url)
        if pjs.getResource(new_url) is None:
            pjs.manage_addScript(cacheable="False",compression="full",cookable="True",
                                 enabled="True", inline="True",id=new_url)
    else:
        if pjs.getResource(old_url) is None and pjs.getResource(new_url) is None:
            pjs.manage_addScript(cacheable="False",compression="full",cookable="True",
                                 enabled="True", inline="True",id=new_url)


def get_company_info_js_border(portal):
    pjs = portal.portal_javascripts
    if pjs.getResource(ci_url % "yes"):
        return True
    elif pjs.getResource(ci_url % "no"):
        return False
    else:
        return None

class LinkedInConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(ICollectiveLinkedInManagement)
    label = _(u"LinkedIn settings form")
    description = _(u"Setup options of LinkedIn inside your plone")
    form_name = _(u"LinkedIn Settings")

class MissingAction(Exception):
    pass

class LinkedInConfiguration(SimpleItem):
    implements(ICollectiveLinkedInManagement)
    company_insider_widget = FieldProperty(ICollectiveLinkedInManagement['company_insider_widget'])

    def set_action_popup(self,value):
        site = getSite()
        site_actions = getToolByName(site,'portal_actions').site_actions
        if ld_action_id not in site_actions.objectIds():
            # I could not make this code work. Some change on porta_actions :-/
            # site_actions.addAction(ld_action_id,ld_action_id,'','',('View',),'site_actions')
            raise MissingAction('%s action in site_actions is missing' % ld_action_id)
        site_actions[ld_action_id].visible = bool(value)

    def get_action_popup(self):
        site = getSite()
        site_actions = getToolByName(site,'portal_actions').site_actions
        return ld_action_id in site_actions.objectIds() and site_actions[ld_action_id].visible
    action_popup = property(get_action_popup, set_action_popup)

    def set_border(self,value):
        site = getSite()
        add_company_info_js(site,overwrite=True,border=value)

    def get_border(self):
        site = getSite()
        return bool(get_company_info_js_border(site))
    border = property(get_border, set_border)


def form_adapter(context):
    return getUtility(ICollectiveLinkedInManagement, name='linkedin_config', context=context)
