from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class BaseView(BrowserView):
    """Base class to hold useful methods for all our views.
    """
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')()
