# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes import atapi

from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from garbas.forum.config import PROJECTNAME

from garbas.forum import ForumMessageFactory as _
from garbas.forum.interfaces import IForumPost



PostSchema = ATDocumentSchema.copy() + atapi.Schema((
    atapi.TextField(
        name='text',
        storage=atapi.AnnotationStorage(),
        searchable=True,
        # TODO :: default = 'getDefaultText', should be aware of quoting
        default_output_type = 'text/x-html-safe',
        widget = atapi.TextAreaWidget( # TODO :: BBCode widget
            label = _(u'topic_label_text', default=u'Text'),
            description = _(u'topic_help_text', default='Write text.'),
        ),
    ),
))

PostSchema['title'].storage = atapi.AnnotationStorage()
PostSchema['title'].default = 'getDefaultTitle'
PostSchema['description'].storage = atapi.AnnotationStorage()
PostSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}

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

    def getDefaultTitle(self):
        return 'RE: ' + self.getParentNode().Title()
   
atapi.registerType(ForumPost, PROJECTNAME)



