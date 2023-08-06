# -*- coding: utf-8 -*-

from datetime import datetime

from Acquisition import aq_inner

from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.component import getUtility

from kss.core import kssaction
from plone.memoize.instance import memoize
from plone.app.layout.viewlets import common
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.layout.globals.interfaces import IViewView
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from collective.captcha.browser.captcha import Captcha

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import Batch

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

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

    def render_template(self):
        return 'garbas.forum.forum_view' 
  
    def has_permissions_to_addtopic(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission("Forum: Submit New Post", self.context) and \
                  self.context.allow_addtopic

    def has_topics(self):
      return len(self.topics()) > 0

    def has_subforums(self):
      return len(self.subforums()) > 0

    @memoize
    def topics(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return [dict(
                 title          = topic.Title,
                 url            = topic.getURL(),
                 author         = topic.Creator,
                 created        = topic.created,
                 replies        = topic.forum_posts,
                 last_author    = len(topic.forum_info)==2 and topic.forum_info[0] or '',
                 last_post_url  = len(topic.forum_info)==2 and self.context.absolute_url()+\
                                                               '/'+topic.getId+\
                                                               topic.forum_info[1] or '',
                 last_post_date = topic.modified,)
            for topic in catalog(
                 object_provides = IForumTopic.__identifier__,
                 path = dict(query='/'.join(self.context.getPhysicalPath()),
                             depth=1),
                 sort_on = getattr(self.request, 'topic.sort_on', 'modified'),
                 sort_order = getattr(self.request, 'topic.sort_order', 'reverse'))]
    
    def topics_batch(self):
        return Batch(self.topics(),
            getattr(self.request, 'b_size', 20),
            getattr(self.request, 'b_start', 0),
            orphan=1)


    @memoize
    def subforums(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        uncategorizes_forums = _(u'uncategorizes_forums', default='Uncategorized')

        sorting = getattr(self.request, 'subforum.sort_on', 'modified')
        sorting_order = getattr(self.request, 'subforum.sort_order', 'reverse')

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
                title           = forum.Title,
                url             = forum.getURL(),
                description     = forum.Description,
                topics          = forum.forum_topics,
                posts           = forum.forum_posts+forum.forum_topics,
                last_author     = len(forum.forum_info)==2 and forum.forum_info[0] or '',
                last_post_url   = len(forum.forum_info)==2 and self.context.absolute_url()+\
                                                               '/'+forum.getId+\
                                                               forum.forum_info[1] or '',
                last_post_date  = forum.modified))
        categories = self.context.categories + (uncategorizes_forums, )
        subforums = []
        for category in categories:
            if not forums.has_key(category): continue
            subforums.append(dict(
                title=category,
                forums=forums[category],))
        return subforums
           

class ForumForm(object):

    def validate(self):
        errors = {}
        for method in dir(self):
            if method[:9] == 'validate_':
                method = getattr(self, method, False)
                if method:
                    tmp_err = method()
                    if tmp_err:
                        errors.update(tmp_err)
        return errors

    def generateNewId(self, title):
        URLNormalizer = IUserPreferredURLNormalizer(self.request)
        id = URLNormalizer.normalize(title)
        def findId(id, i=1):
            if getattr(self.context, id+'-'+str(i), 'expected')!='expected':
                return findId(id, i+1)
            else:
                return id+'-'+str(i)
        if getattr(self.context, id, 'expected')!='expected':
            id = findId(id)
        return id

    def notifySubscribers(self, subject, body):
        host = self.context.MailHost
        notification = IForumNotification(self.context)
        portal = getUtility(ISiteRoot)
        mail_encoding = portal.getProperty('email_charset')
        portal_from = '"' + str(portal.getProperty('email_from_name')) + \
                      '" <' + str(portal.getProperty('email_from_address')) + '>'
        
        mail = MIMEMultipart()
        mail.set_charset(mail_encoding)
        mail['From'] = portal_from
        mail['Date'] = formatdate(localtime=True)
        mail['Subject'] = subject.encode(mail_encoding)
        mail.attach(MIMEText(body.encode(mail_encoding), 'html'))
        
        for email in notification.email_list():
            mail['To'] = email
            host.send(mail.as_string().encode(mail_encoding))


class ForumAddTopic(BrowserContentView, ForumForm):
    """ add topic form """
    
    errors = dict()
    render = ViewPageTemplateFile('templates/add_topic.pt')
   
    def render_template(self):
        return 'garbas.forum.add_topic' 

    def update(self):
        """ all action happens here """

        if self.request.get('form.button.cancel', None):
            self.request.response.redirect(self.context.absolute_url())
        elif self.request.get('form.button.submit', None):
            self.errors = self.validate()
            if not self.errors:
                membership = getToolByName(self.context, 'portal_membership')
                utils = getToolByName(self.context, 'plone_utils')
                transforms = getToolByName(self.context, 'portal_transforms')
                
                types = getToolByName(self.context, 'portal_types')
                factory = types.getTypeInfo('ForumTopic')
                if factory is None:
                    raise Exception, 'Wrong type defined.'
                
                topic_title = getattr(self.request, 'topic_title', None)
                topic_id = self.generateNewId(topic_title)
                topic_text = getattr(self.request, 'topic_text', None)
                topic_text = transforms('text_to_html', topic_text)
                topic_author = membership.getAuthenticatedMember()

                topic = factory._constructInstance(self.context, topic_id)
                topic.title = topic_title
                topic.text  = topic_text
                factory._finishConstruction(topic)

                if self.request.get('notify_me', None)=='1':
                    IForumNotification(topic).subscribe(topic_author.getProperty('email'))

                utils.addPortalMessage(TOPIC_SUCCESS, request=self.request)
                self.request.response.redirect(topic.absolute_url())
    
    def validate_title(self):
        if 'topic_title' not in self.request or \
           not self.request['topic_title']:
            self.errors['topic_title'] = TOPIC_TITLE_ERROR

    def validate_text(self):
        if 'topic_text' not in self.request or \
           not self.request['topic_text']:
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



