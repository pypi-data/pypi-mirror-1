from zope.interface import Interface
from zope import schema

from plone.app.portlets.interfaces import IColumn

from collective.portletpage import MessageFactory as _

class IPortletPage(Interface):
    """Content type interface for portlet pages
    """
    
    title = schema.TextLine(title=_(u"Page title"))
    subtitle = schema.TextLine(title=_(u"Page sub-title"))
    text = schema.Text(title=_(u"Body text"))
    
class IPortletPageColumn(IColumn):
    """Marker interface describing columns on a portlet page
    """
