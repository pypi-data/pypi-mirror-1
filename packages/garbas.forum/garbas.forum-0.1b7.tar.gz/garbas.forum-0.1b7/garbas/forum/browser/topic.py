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

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

from garbas.forum.browser import BrowserContentView
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
   
    def __init__(self, context, request, view=None):
        BrowserContentView.__init__(self, context, request, view)
        self.request.set('disable_border', 1)

    def render_template(self):
        return 'garbas.forum.topic_view' 

    def is_manager(self):
        membership = getToolByName(self.context, 'portal_membership')
        member = membership.getAuthenticatedMember()
        return 'Manager' in member.getRolesInContext(self.context)
    
    def has_permissions_to_addposts(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.checkPermission("Forum: Add ForumPost", self.context)

    def has_posts(self):
        return len(self.posts()) > 0

    @memoize
    def posts(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        membership = getToolByName(self.context, 'portal_membership')

        b_size = getattr(self.request, 'b_size', 20)
        b_start = getattr(self.request, 'b_start', 0)

        result = [ dict( title        = 'RE: ' + self.context.title,
                         UID          = item.UID,
                         author       = item.Creator and item.Creator or 'Anon',
                         author_url   = self.site_url+'/author/'+str(item.Creator),
                         portrait_url = membership.getPersonalPortrait(item.Creator).absolute_url(),
                         created      = item.created,
                         text         = item.getObject().text )
                   for item in catalog(
                         object_provides = IForumPost.__identifier__,
                         path            = dict(query='/'.join(self.context.getPhysicalPath()),
                                                depth=1),
                         sort_on         = 'modified',)]

        return Batch([dict( title        = self.context.title,
                            UID          = self.context.UID(),
                            author       = self.context.Creator(),
                            author_url   = self.site_url+'/author/'+str(self.context.Creator()),
                            portrait_url = membership.getPersonalPortrait(self.context.Creator()).absolute_url(),
                            created      = self.context.CreationDate(),
                            text         = self.context.text )] + result, b_size, b_start, orphan=1)


class ForumAddPost(BrowserContentView):
    """ add post form """
    
    errors = dict()
    render = ViewPageTemplateFile('templates/add_post.pt')
   
    def __init__(self, context, request, view=None):
        BrowserContentView.__init__(self, context, request, view)
        self.request.set('disable_border', 1)

    def render_template(self):
        return 'garbas.forum.add_post' 

    def update(self):
        """ all action happens here """
        
        if getattr(self.request, 'unsubscribe', None):
            member = '' 
            self.unsubscribe(member)


        elif getattr(self.request, 'form.button.submit', None):

            # VALIDATE FIELDS
            self.errors = {}
            for method in dir(self):
                if method[:9] == 'validate_':
                    method = getattr(self, method, False)
                    if method:
                        errors = method()
                        if errors:
                            self.errors.update(errors)

            if not self.errors:
                transforms = getToolByName(self.context, 'portal_transforms')
                catalog = getToolByName(self.context, 'portal_catalog')
                text = getattr(self.request, 'post_text', None)
                old_text = text
                text = transforms('text_to_html', text)

                normalizer = IUserPreferredURLNormalizer(self.request)
                title = 'RE: '+self.context.title
                title.decode('utf-8')
                if not isinstance(title, unicode):
                    title = unicode(title, 'utf-8')
                post_id = normalizer.normalize('RE: '+title)
 
                def validId(i):
                    if getattr(self.context, post_id+'-'+str(i), 'krneki') != 'krneki':
                        return validId(i+1)
                    return post_id+'-'+str(i)
 
                if getattr(self.context, post_id, 'krneki') != 'krneki':
                    post_id = validId(1)

                self.context.invokeFactory('ForumPost',
                          id    = post_id,
                          title = 'RE: '+self.context.title,
                          text  = text)
                post = getattr(self.context, post_id)

                notify(ObjectModifiedEvent(post))

                portal = getUtility(ISiteRoot)
                language = getToolByName(self.context, 'portal_languages')
                membership = getToolByName(self.context, 'portal_membership')
                localization_code = language.getLanguageBindings()[0]
                mail_encoding = portal.getProperty('email_charset')
                portal_from = '"' + str(portal.getProperty('email_from_name')) + \
                              '" <' + str(portal.getProperty('email_from_address')) + '>'
                author = ''
                author_catalog = catalog(object_provides=IMember.__identifier__,
                                         content_email = post.Creator())
                if len(author_catalog) == 1:
                    author = author_catalog[0].Title

                member = str(membership.getAuthenticatedMember())
                if member:
                    IForumNotification(self.context).subscribe(member)
  
                mail = MIMEMultipart()
                mail.set_charset(mail_encoding)
                mail['From'] = portal_from
                mail['Date'] = formatdate(localtime=True)
                mail['Subject'] = translate('mail_notify_change_subject',
                    domain = 'garbas.forum',
                    mapping = dict(topic=self.context.title),
                    target_language = localization_code,
                    context = self.context).encode(mail_encoding)
                mail.attach( MIMEText( translate( 'mail_notify_change_text',
                    domain = 'garbas.forum',
                    mapping = dict(title  = post.title,
                                   text   = old_text,
                                   link   = post.absolute_url(),
                                   author = author),
                    target_language = localization_code,
                    context = self.context).encode(mail_encoding)))

                host = self.context.MailHost
                emails = IForumNotification(self.context).notification_emails()
                for email in emails:
                    if email == post.Creator():
                        continue
                    mail['To'] = email
                    host.send(mail.as_string().decode(mail_encoding).encode(mail_encoding))
            
                # FIXME :: portal_status_message si not working
                self.request.response.redirect(
                    #self.site_url + '/' + \
                    post.absolute_url() + '/' + \
                    '?portal_status_messages=' + POST_SUCCESS)

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




