"""This package contains views for the content area of your page.
"""

import Acquisition
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.skinny.base import BaseView

class DefaultView(BaseView):
    """A view for the content area that's used when no other view was
    found.
    """
    def __call__(self):
        return ("<strong>Could not find a view for %r.  You can add one "
                "in the content.py file.</strong>" % self.context.portal_type)

class PageView(BaseView):
    __call__ = ViewPageTemplateFile('templates/content/page.pt')

class Registry(BaseView):
    """This view implements a very simple look-up mechanism based on
    the portal type and a dict.  Use adaptation instead if you're
    feeling clever.
    """
    # Our simple registry of {portal_type: BrowserView}
    views = {
        'Document': PageView,
        }

    def __call__(self):
        # Try to look up the default page for context first
        default_name = getattr(
            Acquisition.aq_base(self.context), 'default_page', '')
        if default_name:
            self.context = Acquisition.aq_inner(
                getattr(self.context, default_name))

        view = self.views.get(self.context.portal_type, DefaultView)
        return view(self.context, self.request).__of__(self.context)()
