# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.exceptions import AccessControl_Unauthorized

from garbas.forum.content.base import ForumFolder
from garbas.forum.content.base import ForumFolderSchema
from garbas.forum.interfaces import IForumTopic
from garbas.forum.interfaces import IForum
from garbas.forum.config import PROJECTNAME
from garbas.forum import ForumMessageFactory as _


TopicSchema = ForumFolderSchema.copy() + atapi.Schema((
    atapi.TextField(
        name='text',
        required = True,
        searchable=True,
        default_output_type = 'text/x-html-safe',
        storage=atapi.AnnotationStorage(),
        widget = atapi.TextAreaWidget( # TODO :: BBCode widget
            label = _(u'topic_label_text', default=u'Text'),
            description = _(u'topic_help_text', default='Write text.'),
        ),
    ),
))
TopicSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}


class ForumTopic(ForumFolder):
    """forum topic content"""

    implements(IForumTopic)

    portal_type = "ForumTopic"
    schema = TopicSchema
    
    title       = atapi.ATFieldProperty('title')
    text        = atapi.ATFieldProperty('text')
   
atapi.registerType(ForumTopic, PROJECTNAME)


