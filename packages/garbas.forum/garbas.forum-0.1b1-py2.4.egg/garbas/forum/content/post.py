# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes import atapi

from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from garbas.forum.config import PROJECTNAME

from garbas.forum import ForumMessageFactory as _
from garbas.forum.interfaces import IForumPost



PostSchema = ATDocumentSchema.copy()

PostSchema['title'].storage = atapi.AnnotationStorage()
PostSchema['description'].storage = atapi.AnnotationStorage()
PostSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}
PostSchema['text'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(PostSchema)


class ForumPost(ATDocument):
    """forum post content
    """
    implements(IForumPost)
    
    portal_type = "ForumPost"
    _at_rename_after_creation = True
    schema = PostSchema
    
    title = atapi.ATFieldProperty('title')
    text = atapi.ATFieldProperty('text')

atapi.registerType(ForumPost, PROJECTNAME)



