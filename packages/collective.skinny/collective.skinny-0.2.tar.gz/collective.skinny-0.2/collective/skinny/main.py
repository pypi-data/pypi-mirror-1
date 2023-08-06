"""This package contains the ``Main`` view, which is the entry point
into your skin.  The equivalent to Plone's 'main template' can be found
at ``templates/main.pt``
"""

from AccessControl import getSecurityManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.permissions import View

from collective.skinny.base import BaseView
import collective.skinny.content
import collective.skinny.fourohfour

class Head(BaseView):
    __call__ = ViewPageTemplateFile('templates/head.pt')

class Main(BaseView):
    __call__ = ViewPageTemplateFile('templates/main.pt')

    # Part definitons {name: BrowserView}
    parts = {
        'head': Head,
        'content': collective.skinny.content.Registry,
        }

    def get_part(self, name):
        """Returns snippets for use in the main template.

        You can add more snippets to the ``parts`` dict.
        """
        return self.parts[name](
            self.context, self.request).__of__(self.context)()
