# -*- coding: utf-8 -*-

from datetime import datetime

from Acquisition import aq_inner

from zope.interface import alsoProvides
from zope.component import getMultiAdapter

from kss.core import kssaction
from plone.memoize.instance import memoize 
from plone.app.layout.viewlets import common
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.layout.globals.interfaces import IViewView
from collective.captcha.browser.captcha import Captcha

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import Batch

from garbas.forum.browser import BrowserContentView
from garbas.forum.interfaces import IForum
from garbas.forum.interfaces import IForumTopic
from garbas.forum.interfaces import IForumNotification
from garbas.forum import ForumMessageFactory as _


TOPIC_SUCCESS     = _(u'topic_success', default='Topic was successfuly added.')
TOPIC_TITLE_ERROR = _(u'topic_title_error', default='Subject is required. Please correct.')
TOPIC_TEXT_ERROR  = _(u'topic_text_error', default='Text is required. Please correct.')
CAPTCHA_ERROR    = _(u'captcha_error', default=u'Captcha is required. Please correct.')
CAPTCHA_ERROR2   = _(u'captcha_error2', default=u'Captcha is incorrect.')


class ForumView(BrowserContentView):
    """ forum main view """

    render = ViewPageTemplateFile('templates/forum.pt')

    def __init__(self, context, request, view=None):
        BrowserContentView.__init__(self, context, request, view)
        self.request.set('disable_border', 1)

    def render_template(self):
        return 'garbas.forum.forum_view' 
  
    def is_manager(self):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getAuthenticatedMember()
        return 'Manager' in member.getRolesInContext(self.context)

    def has_permissions_to_addtopic(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission("Forum: Add ForumTopic", self.context) and \
                  self.context.allow_addtopic

    def has_topics(self):
      return len(self.topics()) > 0

    def has_subforums(self):
      return len(self.subforums()) > 0

    @memoize
    def topics(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        
        sorting = getattr(self.request, 'garbas.forum.topics.sorting', 'forum_last_post_date')
        sorting_order = getattr(self.request, 'garbas.forum.topics.sorting_order', 'reverse') 

        b_size = getattr(self.request, 'b_size', 20)
        b_start = getattr(self.request, 'b_start', 0)

        results = [
                  dict(
                      title = topic.Title,
                      url = self.context.absolute_url()+'/'+str(topic.id),
                      author = topic.Creator,
                      author_url = self.site_url+'/author/'+str(topic.Creator),
                      created = topic.created,
                      replies = topic.forum_posts,
                      last_post_author = topic.forum_last_post_author,
                      last_post_author_url = self.site_url+'/author/'+str(topic.forum_last_post_author), 
                      last_post_url = self.site_url+str(topic.forum_last_post_url),
                      last_post_date = topic.forum_last_post_date,
                  )

                  for topic in catalog(
                      object_provides=IForumTopic.__identifier__,
                      path=dict(query='/'.join(self.context.getPhysicalPath()),
                                depth=1),
                      sort_on=sorting,
                      sort_order=sorting_order,)
               ]
        return Batch(results, b_size, b_start, orphan=1)


    @memoize
    def subforums(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        uncategorizes_forums = _(u'uncategorizes_forums', default='Uncategorized')

        sorting = getattr(self.request, 'garbas.forum.subforums-sorting', 'forum_last_post_date')
        sorting_order = getattr(self.request, 'garbas.forum.subforums-sorting_order', 'reverse') 

        forums = {}
        for forum in catalog(object_provides=IForum.__identifier__,
                             path=dict(query='/'.join(self.context.getPhysicalPath()),depth=1),
                             sort_on=sorting,
                             sort_order=sorting_order,):
            if forum.forum_category in self.context.categories: 
                category = forum.forum_category
            else: 
                category = uncategorizes_forums
            
            if not forums.has_key(category):
                forums[category] = []
            forums[category].append(dict(
                    title = forum.Title,
                    url = self.context.absolute_url()+'/'+str(forum.id),
                    description = forum.Description,
                    topics = forum.forum_topics,
                    posts = forum.forum_posts+forum.forum_topics,
                    last_post_author = forum.forum_last_post_author,
                    last_post_author_url = self.site_url+'/author/'+str(forum.forum_last_post_author), 
                    last_post_url = self.site_url+str(forum.forum_last_post_url),
                    last_post_date = forum.forum_last_post_date,
                ))
        categories = self.context.categories + (uncategorizes_forums, )
        subforums = []
        for category in categories:
            if not forums.has_key(category): continue
            subforums.append(dict(
                title=category,
                forums=forums[category],))
        
        return subforums
            

class ForumAddTopic(BrowserContentView):
    """ add topic form """
    
    errors = dict()
    render = ViewPageTemplateFile('templates/add_topic.pt')
   
    def __init__(self, context, request, view=None):
        BrowserContentView.__init__(self, context, request, view)
        self.request.set('disable_border', 1)

    def render_template(self):
        return 'garbas.forum.add_topic' 

    def update(self):
        """ all action happens here """

        if getattr(self.request, 'form.button.submit', None):
            # VALIDATE FIELDS
            for method in dir(self):
                if method[:9] == 'validate_':
                    method = getattr(self, method, False)
                    if method:
                        method()

            title = getattr(self.request, 'topic_title', None)
            text = getattr(self.request, 'topic_text', None)

            now = datetime.today()
            topic_id = self.context.invokeFactory('ForumTopic', 
                        id=now.strftime('forumtopic_%Y-%m-%d.')+str(now.microsecond),
                        title=title, 
                        text=text)
            topic = getattr(self.context, topic_id)
            topic._renameAfterCreation()
            
            membership = getToolByName(self.context, 'portal_membership')
            member = str(membership.getAuthenticatedMember())
            IForumNotification(topic).subscribe(member)

            # FIXME :: portal_status_message si not working
            self.request.response.redirect(
                topic.absolute_url() + '/' + \
                '?portal_status_messages=' + TOPIC_SUCCESS)

    def validate_title(self):
        if 'topic_title' not in self.request or \
           self.request['topic_title']:
            self.errors['topic_title'] = TOPIC_TITLE_ERROR

    def validate_text(self):
        if 'topic_text' not in self.request or \
           self.request['topic_text']:
            self.errors['topic_text'] = TOPIC_TEXT_ERROR

    def validate_captcha(self):
        if not self.is_anonymous(): return
        if 'captcha' not in self.request or \
           not self.request['captcha']:
            self.errors['captcha'] = CAPTCHA_ERROR 
        elif not Captcha(self.context, self.request).verify(self.request['captcha']):
            self.errors['captcha'] = CAPTCHA_ERROR2
        
    def is_anonymous(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.isAnonymousUser()

    def captcha(self):
        return Captcha(self.context, self.request)



