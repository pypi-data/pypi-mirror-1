# -*- coding: utf-8 -*-

from zope.i18n import translate
from zope.event import notify
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.lifecycleevent import ObjectModifiedEvent
from plone.memoize.instance import memoize
from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
from collective.captcha.browser.captcha import Captcha

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import Batch
from Products.CMFCore.interfaces import ISiteRoot

from garbas.forum.browser import BrowserContentView
from garbas.forum.browser.forum import ForumForm
from garbas.forum.interfaces import IForumPost
from garbas.forum.interfaces import IForumNotification
from garbas.forum import ForumMessageFactory as _

from lajf.login.interfaces import IMember

POST_SUCCESS        = _(u'post_success', default='Post was successfuly added.')
POST_TITLE_ERROR    = _(u'post_title_error', default='Subject is required. Please correct.')
POST_TEXT_ERROR     = _(u'post_text_error', default='Text is required. Please correct.')
CAPTCHA_ERROR       = _(u'captcha_error', default=u'Captcha is required. Please correct.')
CAPTCHA_ERROR2      = _(u'captcha_error2', default=u'Captcha is incorrect.')
UNSUBSCRIBE_SUCCESS = _(u'unsubscribe_success', default=u'Successfully unsubscribed.')
UNSUBSCRIBE_ERROR   = _(u'unsubscribe_error', default=u'There was error when unsubscribing. Please contact administrator.')
SUBSCRIBE_SUCCESS   = _(u'subscribe_success', default=u'Successfully subscribed.')
SUBSCRIBE_ERROR     = _(u'subscribe_error', default=u'There was error when subscribing. Please contact administrator.')

class ForumTopicView(BrowserContentView):
    """ topic view """

    errors = dict()
    render = ViewPageTemplateFile('templates/topic.pt')
   
    def render_template(self):
        return 'garbas.forum.topic_view' 

    def update(self):
        utils = getToolByName(self.context, 'plone_utils')
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getAuthenticatedMember()

        if self.request.get('subscribe', None)=='1':
            if member:
                IForumNotification(self.context).subscribe(member.getProperty('email'))
                utils.addPortalMessage(SUBSCRIBE_SUCCESS, request=self.request)
            else:
                utils.addPortalMessage(SUBSCRIBE_ERROR, 'error', request=self.request)
            self.request.response.redirect(self.context.absolute_url())
        elif self.request.get('unsubscribe', None)=='1':
            if member:
                IForumNotification(self.context).unsubscribe(member.getProperty('email'))
                utils.addPortalMessage(UNSUBSCRIBE_SUCCESS, request=self.request)
            else:
                utils.addPortalMessage(UNSUBSCRIBE_ERROR, 'error', request=self.request)
            self.request.response.redirect(self.context.absolute_url())
    
    @memoize
    def subscribe_list(self):
        return IForumNotification(self.context).email_list()

    def is_subscribed(self):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getAuthenticatedMember()
        return member.getProperty('email') in self.subscribe_list()

    @memoize
    def has_permissions_to_addposts(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission("Forum: Submit New Post", self.context)

    def has_posts(self):
        return len(self.posts()) > 0

    @memoize
    def posts(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        membership = getToolByName(self.context, 'portal_membership')

        b_size = getattr(self.request, 'b_size', 20)
        b_start = getattr(self.request, 'b_start', 0)

        result = [ dict( title        = item.Title,
                         UID          = item.UID,
                         author       = item.Creator and item.Creator or '',
                         portrait_url = membership.getPersonalPortrait(item.Creator).absolute_url(),
                         created      = item.created,
                         text         = item.getObject().text ) # TODO :: maybe put it in catalog
                   for item in catalog(
                         object_provides = IForumPost.__identifier__,
                         path            = dict(query='/'.join(self.context.getPhysicalPath()),
                                                depth=1),
                         sort_on         = 'modified',)]

        return Batch([dict( title        = self.context.title,
                            UID          = self.context.UID(),
                            author       = self.context.Creator(),
                            portrait_url = membership.getPersonalPortrait(self.context.Creator()).absolute_url(),
                            created      = self.context.CreationDate(),
                            text         = self.context.text )] + result, b_size, b_start, orphan=1)


class ForumAddPost(BrowserContentView, ForumForm):
    """ add post form """
    
    errors = dict()
    render = ViewPageTemplateFile('templates/add_post.pt')
   
    def render_template(self):
        return 'garbas.forum.add_post' 

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
                factory = types.getTypeInfo('ForumPost')
                if factory is None:
                    raise Exception, 'Wrong type defined.'
                
                post_title = getattr(self.request, 'post_title', None)
                post_id = self.generateNewId(post_title)
                post_text = getattr(self.request, 'post_text', None)
                post_text = transforms('text_to_html', post_text)
                post_author = membership.getAuthenticatedMember()
                
                post_author_name = ''
                if post_author:
                    post_author_name = post_author.getProperty('fullname')

                post = factory._constructInstance(self.context, post_id)
                post.title = post_title
                post.text  = post_text
                factory._finishConstruction(post)

                self.notifySubscribers(
                    subject = translate(_(u'mail_notify_change_subject',
                        default=u'New reply on ${topic_title}',
                        mapping=dict(topic_title=self.context.Title()))),
                    body    = translate(_(u'mail_notify_change_text',
                        default='''
                            <a href="${post_url}">
                                <b>${post_title}</b>
                            </a><br />by ${post_author}
                            <p>${post_text}</p>
                            <br />
                            --- Unsubscribe here: <a href="${unsubscribe}">${unsubscribe}</a>''',
                        mapping=dict(post_title=post_title,
                                     post_url=post.absolute_url(),
                                     post_author=post_author_name,
                                     post_text=post_text,
                                     unsubscribe=self.context.absolute_url()+'/?unsubscribe=1'))))
                
                if self.request.get('notify_me', None)=='1':
                    IForumNotification(self.context).subscribe(post_author.getProperty('email'))

                utils.addPortalMessage(POST_SUCCESS, request=self.request)
                self.request.response.redirect(post.absolute_url())

    def validate_title(self):
        if 'post_title' not in self.request or \
           not self.request['post_title']:
            self.errors['post_title'] = POST_TITLE_ERROR

    def validate_text(self):
        if 'post_text' not in self.request or \
           not self.request['post_text']:
            self.errors['post_text'] = POST_TEXT_ERROR

    def validate_captcha(self):
        membership = getToolByName(self.context, 'portal_membership')
        if not membership.isAnonymousUser(): return
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

    @memoize
    def subscribe_list(self):
        return IForumNotification(self.context).email_list()

    def is_subscribed(self):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getAuthenticatedMember()
        return member.getProperty('email') in self.subscribe_list()


