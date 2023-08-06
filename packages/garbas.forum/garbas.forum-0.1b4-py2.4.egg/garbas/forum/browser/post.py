# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ForumPostView(BrowserView):

    def __call__(self, *argv, **kw):
        context = aq_inner(self.context)
        request = self.request

        parent = context.getParentNode()
        redirect_url = parent.absolute_url()+'#'+context.UID()

        return request.RESPONSE.redirect(redirect_url)


