# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import getMultiAdapter
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema
from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from garbas.forum import ForumMessageFactory as _
from garbas.forum.interfaces import IForumTopic
from garbas.forum.interfaces import IForumPost
from garbas.forum.interfaces import IForum


ForumFolderSchema = ATBTreeFolderSchema.copy()
ForumFolderSchema['title'].storage = atapi.AnnotationStorage()
ForumFolderSchema['description'].storage = atapi.AnnotationStorage()
ForumFolderSchema['description'].widget.visible = {'view': 'hidden', 'edit': 'hidden' }

class ForumFolder(ATBTreeFolder):
    """forum folder"""

    _at_rename_after_creation = True

    schema = ForumFolderSchema 
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def last_post(self):
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog(object_provides=IForumPost.__identifier__,
                              path=dict(query='/'.join(self.getPhysicalPath())),
                              sort_on='created',
                              sort_order='reverse',
                              sort_limit=1,)[:1]
        if result: 
          return result[0]

    def last_topic(self):
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog(object_provides=IForumTopic.__identifier__,
                              path=dict(query='/'.join(self.getPhysicalPath())),
                              sort_on='created',
                              sort_order='reverse',
                              sort_limit=1,)[:1]
        if result: 
          return result[0]

    security.declarePublic('forum_category')
    def forum_category(self):
        """forum category"""
        return getattr(self, 'category', None)
            
    security.declarePublic('forum_topics')
    def forum_topics(self):
        """number of all topics"""
        catalog = getToolByName(self, 'portal_catalog')
        return len(catalog(object_provides=IForumTopic.__identifier__,
                                path=dict(query='/'.join(self.getPhysicalPath()),),))
            
    security.declarePublic('forum_posts')
    def forum_posts(self):
        """number of all posts"""
        catalog = getToolByName(self, 'portal_catalog')
        return len(catalog(object_provides=IForumPost.__identifier__,
                                path=dict(query='/'.join(self.getPhysicalPath()),),))
            
    security.declarePublic('forum_last_post_date')
    def forum_last_post_date(self):
        """last post date"""
        last_post_date = getattr(self.last_post(), 'created', None)
        if not last_post_date:
            last_post_date = getattr(self.last_topic(), 'created', None)
        return last_post_date


    security.declarePublic('forum_last_post_author')
    def forum_last_post_author(self):
        """last post author"""
        last_post_author = getattr(self.last_post(), 'Creator', None)
        if not last_post_author:
            last_post_author = getattr(self.last_topic(), 'Creator', None)
        return last_post_author

    security.declarePublic('forum_last_post_url')
    def forum_last_post_url(self):
        """last post url"""
        last_post = self.last_post()
        if not last_post:
            last_post = self.last_topic()
        if last_post: 
            portal = getToolByName(self, 'portal_url').getPortalObject()
            site_url = portal.absolute_url()
            return last_post.getObject().absolute_url()[len(site_url):]
        return None

def reindex_for_topics(context, event):
    """reindex all sub-forum folders"""
    parent = context.getParentNode()
    while parent.__providedBy__(IForum):
        parent.reindexObject(['forum_topics',])
        parent = parent.getParentNode()

def reindex_for_posts(context, event):
    """reindex all sub-forum folders"""
    parent = context.getParentNode()
    while parent.__providedBy__(IForum) or parent.__providedBy__(IForumTopic):
        parent.reindexObject(['forum_posts','forum_last_post_author', 'forum_last_post_date', 'forum_last_post_url',])
        parent = parent.getParentNode()

    
