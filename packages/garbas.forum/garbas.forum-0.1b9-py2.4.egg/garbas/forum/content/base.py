# -*- coding: utf-8 -*-

from DateTime import DateTime
from Acquisition import aq_inner
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


class ForumFolder(ATBTreeFolder):
    """forum folder"""

    _at_rename_after_creation = True
    schema = ForumFolderSchema

    def _getLastPost(self):
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog(
            object_provides = IForumPost.__identifier__,
            path            = dict(query='/'.join(self.getPhysicalPath())),
            sort_on         = 'created',
            sort_order      = 'reverse',
            sort_limit      = 1,)
        if result:
            return result[0].getObject()

    def _getLastTopic(self):
        catalog = getToolByName(self, 'portal_catalog')
        result = catalog(
            object_provides = IForumTopic.__identifier__,
            path            = dict(query='/'.join(self.getPhysicalPath())),
            sort_on         = 'created',
            sort_order      = 'reverse',
            sort_limit      = 1,)
        if result:
          return result[0].getObject()

    # CATALOG INDEXES
    def forum_category(self):
        """forum category"""
        return getattr(self, 'category', '')
            
    def forum_topics(self):
        """number of all topics"""
        catalog = getToolByName(self, 'portal_catalog')
        return len(catalog(
            object_provides = IForumTopic.__identifier__,
            path            = dict(query='/'.join(self.getPhysicalPath()))))
            
    def forum_posts(self):
        """number of all posts"""
        catalog = getToolByName(self, 'portal_catalog')
        return len(catalog(
            object_provides = IForumPost.__identifier__,
            path            = dict(query='/'.join(self.getPhysicalPath()))))
            
    def modified(self):
        """last post date"""
        last_post = self._getLastPost()
        if not last_post:
            last_post = self._getLastTopic()
        return last_post!=None and last_post.created() or self.created()

    def forum_info(self):
        last_post = self._getLastPost()
        if not last_post:
            last_post = self._getLastTopic()
        return [last_post!=None and last_post.Creator() or '',
                last_post!=None and last_post.absolute_url()[len(self.absolute_url()):] or '']


def reindex_for_topics(context, event):
    """reindex all sub-forum folders"""
    def reindex_parent(context):
        parent = aq_inner(context.getParentNode())
        if IForum.providedBy(parent) or \
           IForumTopic.providedBy(parent):
            parent.reindexObject(['forum_topics',
                                  'modified',
                                  'forum_info',])
            reindex_parent(parent)
    reindex_parent(context)

def reindex_for_posts(context, event):
    """reindex all sub-forum folders"""
    def reindex_parent(context):
        parent = aq_inner(context.getParentNode())
        if IForum.providedBy(parent) or \
           IForumTopic.providedBy(parent):
            parent.reindexObject(['forum_posts',
                                  'modified',
                                  'forum_info',])
            reindex_parent(parent)
    reindex_parent(context)

