from zope import schema
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlet.static.static import IStaticPortlet

from collective.linkedin import LinkedInMessageFactory as _


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ICollectiveLinkedInManagement(Interface):
    """
    """
    company_insider_widget = schema.TextLine(
        title = _(u"Company Insider Widget"),
        required = False,
        description = _(u"Enter the company name"),
    )

    action_popup = schema.Bool(
        title = _(u"Site action pop up"),
        required = False,
        description = _(u"Check it if you want the site action popup"),
    )

    border = schema.Bool(
        title = _(u"Border"),
        required = False,
        description = _(u"Caution: if you enable popup, this needs to be checked."),
    )

class ICompanyInfoPortlet(IStaticPortlet):
    """ Defines a new portlet "Company Info" which takes properties of the existing static text portlet. """
    pass

class IProfileInfoPortlet(IPortletDataProvider):
    """ Defines a new portlet "Profile Info" """
    profile_id = schema.TextLine(
            title=_(u"LinkedIn user id"),
            description=_(u"Id of the LinkedIn user to show information"),
            default=u"",
            required=True)
    name = schema.TextLine(
            title=_(u"LinkedIn Name"),
            description=_(u"The name of the person"),
            default=u"",
            required=True)
