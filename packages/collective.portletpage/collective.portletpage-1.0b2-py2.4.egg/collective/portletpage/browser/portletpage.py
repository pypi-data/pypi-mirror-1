from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Base(BrowserView):
    """Base class for index page views
    """

class TwoColumns(Base):
    """A two-column layout.
    """
    
    __call__ = ViewPageTemplateFile('two-columns.pt')