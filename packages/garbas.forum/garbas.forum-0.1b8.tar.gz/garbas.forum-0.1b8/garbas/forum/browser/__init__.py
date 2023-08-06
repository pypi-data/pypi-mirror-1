# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from os.path import basename
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BrowserContentView(BrowserView):
    """ Content Provider for main content area.
        Now its possible that we reload main content area with KSS. """

    __call__ = ViewPageTemplateFile('content_view.pt')
    render = None

    def __init__(self, context, request, view=None):
        self.context = aq_inner(context)
        self.request = request
        if view: 
            self.__parent__ = view

        self.portal_state = getMultiAdapter((self.context, self.request), 
                                                    name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
    
    def update(self):
        """ method that is being call when content provider"""
        pass

    def getPhysicalPath(self):
        """ needed so its possible to do path search over catalog 
              ExtendedPathIndex needs it ... maybe a bug  """
        return self.context.getPhysicalPath()

    def render_template(self):
        """ return name of render template """
        return basename(self.render.filename)[:-3]
    
