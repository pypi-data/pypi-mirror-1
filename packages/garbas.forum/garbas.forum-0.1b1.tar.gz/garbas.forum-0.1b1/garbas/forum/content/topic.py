# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from garbas.forum.content.base import ForumFolder
from garbas.forum.content.base import ForumFolderSchema
from garbas.forum.interfaces import IForumTopic
from garbas.forum.config import PROJECTNAME
from garbas.forum import ForumMessageFactory as _


TopicSchema = ForumFolderSchema.copy() + atapi.Schema((
    atapi.TextField(
        name='text',
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            label = _(u'topic_label_text', default=u'Text'),
            description = _(u'topic_help_text', default='Write text.'),
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload
        ),
        storage=atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        searchable=True,
    ),
))
TopicSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}
finalizeATCTSchema(TopicSchema)


class ForumTopic(ForumFolder):
    """forum topic content"""

    implements(IForumTopic)

    portal_type = "ForumTopic"
    schema = TopicSchema
    
    title       = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text        = atapi.ATFieldProperty('text')
    
atapi.registerType(ForumTopic, PROJECTNAME)


