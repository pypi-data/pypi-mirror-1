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

POST_SUCCESS     = _(u'post_success', default='Post was successfuly added.')
POST_TITLE_ERROR = _(u'post_title_error', default='Subject is required. Please correct.')
POST_TEXT_ERROR  = _(u'post_text_error', default='Text is required. Please correct.')
CAPTCHA_ERROR    = _(u'captcha_error', default=u'Captcha is required. Please correct.')
CAPTCHA_ERROR2   = _(u'captcha_error2', default=u'Captcha is incorrect.')



class ForumTopicView(BrowserContentView):
    """ topic view """

    errors = dict()
    render = ViewPageTemplateFile('templates/topic.pt')
   
    def render_template(self):
        return 'garbas.forum.topic_view' 

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
        
        if getattr(self.request, 'unsubscribe', None):
            member = '' 
            self.unsubscribe(member)

        elif getattr(self.request, 'form.button.submit', None):
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
                        default=u'<a href="${post_url}"><h2>${post_title}</h2></a><p>by ${post_author}</p><p>${post_text}</p>',
                        mapping=dict(post_title=post_title,
                                     post_url=post.absolute_url(),
                                     post_author=post_author_name,
                                     post_text=post_text))))
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

    def unsubscribe(self, member):
        IForumNotification(self.context).unsubscribe(member)




