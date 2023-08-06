from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlet.static import static

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.linkedin.browser.company_info import CompanyInfo
from collective.linkedin.browser.profile_info import ProfileInfo
from collective.linkedin.browser.interfaces import ICompanyInfoPortlet, IProfileInfoPortlet
from collective.linkedin import LinkedInMessageFactory as _

class CompanyInfoRenderer(static.Renderer,CompanyInfo):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('templates/company_info.pt')

class CompanyInfoAssignment(static.Assignment):
    """ Assigner for company info portlet. """
    implements(ICompanyInfoPortlet)

    @property
    def title(self):
        return _(u"Company Info portlet")

class CompanyInfoAddForm(base.NullAddForm):
    """ Make sure that add form creates instances of our custom portlet instead
    of the base class portlet. """
    def create(self):
        return CompanyInfoAssignment()

class CompanyInfoEditForm(base.EditForm):
    form_fields = form.Fields()
    label = _(u"Edit Company Info")
    description = _(u"This portlet displays Company Info.")

class ProfileInfoRenderer(base.Renderer,ProfileInfo):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('templates/profile_info.pt')

class ProfileInfoAssignment(base.Assignment):
    """ Assigner for profile info portlet. """
    implements(IProfileInfoPortlet)

    profile_id = u''
    name = u''

    def __init__(self, name=u"", profile_id=u""):
        self.name = name
        self.profile_id = profile_id

    @property
    def title(self):
        return _(u"Profile Info portlet")

class ProfileInfoAddForm(base.AddForm):
    """ Make sure that add form creates instances of our custom
    portlet instead of the base class portlet. """
    form_fields = form.Fields(IProfileInfoPortlet)
    label = _(u"Add LinkedIn Profile Portlet")
    description = _(u"This portlet display a LinkedIn profile.")

    def create(self, data):
        return ProfileInfoAssignment(name=data.get('name', u''),
                                     profile_id=data.get('profile_id',u''))

class ProfileInfoEditForm(base.EditForm):
    form_fields = form.Fields(IProfileInfoPortlet)
    label = _(u"Edit Profile Info")
    description = _(u"This portlet displays Profile Info.")
