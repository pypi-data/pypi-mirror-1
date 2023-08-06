"""This package contains the ``Main`` view, which is the entry point
into your skin.  The equivalent to Plone's 'main template' can be found
at ``templates/main.pt``
"""

from zope import interface
from zope import component
from zExceptions import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import plone.app.layout.viewlets.common
import plone.postpublicationhook.interfaces

from collective.skinny.base import render_viewlet
from collective.skinny.base import BaseView
from collective.skinny.interfaces import IPublicLayer, IPublicLayerOK

import collective.skinny.content

class MyNavigation(BaseView):
    """An example of a simple navigation implementation that simply
    reuses Plone's GlobalSectionViewlet and the PathBarViewlet.
    """
    def __call__(self):
        html = render_viewlet(
            plone.app.layout.viewlets.common.GlobalSectionsViewlet, self)
        html += render_viewlet( 
            plone.app.layout.viewlets.common.PathBarViewlet, self)
        return html

class Main(BaseView):
    template = ViewPageTemplateFile('templates/main.pt')

    # Part definitions:

    # When in your template, you say ``view/render_content``, we'll
    # first look into the parts dict to see if you have a part
    # registered here.  Otherwise, we'll fall back to looking up a
    # template in the templates directory.  That is, you can put
    # ``spam.pt`` into your templates directly and use it via
    # ``view/render_spam`` without the need of registering anything
    # here:
    parts = {
        'content': collective.skinny.content.Registry,
        'navigation': MyNavigation,
        }

    def __call__(self):
        # Mark the request as OK; it's gone through us:
        interface.alsoProvides(self.request, IPublicLayerOK)
        return self.template()

@component.adapter(interface.Interface,
                   plone.postpublicationhook.interfaces.IAfterPublicationEvent)
def dont_leak(object, event):
    request = event.request

    # Allow any non html resources:
    headers = request.response.headers
    if not headers.get('content-type', '').startswith('text/html'):
        return

    # Everything else needs to have IPublicLayerOK on the request:
    if (IPublicLayer.providedBy(request) and
        not IPublicLayerOK.providedBy(request)):
        raise NotFound()
