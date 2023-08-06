from zope.interface import Interface
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from plone.app.portlets.manager import ColumnPortletManagerRenderer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quintagroup.portletmanager.footer.interfaces import IFooter

class FooterPortletManagerRenderer(ColumnPortletManagerRenderer):
    """Render a footer portlets
    """

    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IFooter)
    template = ViewPageTemplateFile('templates/portlets.pt')
    error_message = ViewPageTemplateFile('templates/error_message.pt')
