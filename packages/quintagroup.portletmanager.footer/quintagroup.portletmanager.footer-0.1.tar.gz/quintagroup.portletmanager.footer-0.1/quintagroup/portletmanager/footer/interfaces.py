from plone.portlets.interfaces import IPortletManager
#from plone.app.portlets.interfaces import IColumn

class IFooter(IPortletManager):
    """ Portlet manager that is rendered in page footer

    Register a portlet for IFooter if it is applicable to page footer.
    """
