# -*- coding: utf-8 -*-

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from garbas.forum.content.base import ForumFolder
from garbas.forum.content.base import ForumFolderSchema
from garbas.forum.interfaces import IForum
from garbas.forum.config import PROJECTNAME
from garbas.forum import ForumMessageFactory as _


ForumSchema = ForumFolderSchema.copy() + atapi.Schema((
    atapi.LinesField(
        name='categories',
        required=False,
        storage = atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label = _(u'categories_label', default=u'Categories'),
            description = _(u'categories_help', default='Write categories (one in each line) in order of appearing.'),
        ),
    ),
    atapi.StringField(
        name='category',
        required=False,
        storage = atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label = _(u'category_label', default=u'Category'),
            description = _(u'category_help', default='Select category in which forum you are just creating, should appear.'),
            format='select',
        ),
        vocabulary='getAvaliableCategories',
    ),
    atapi.BooleanField(
        name='allow_addtopic',
        default=True,
        storage = atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label = _(u'allow_addtopic_label', default=u'Allow to add topic'),
            description = _(u'allow_addtopic_help', default='If checked you are allowing user to add topic to forum. This option is useful when you are creating forum container and you dont want to have any topic inside your container.'),
        ),
    ),
))
finalizeATCTSchema(ForumSchema)


class Forum(ForumFolder):
    """forum content"""

    implements(IForum)

    portal_type = "Forum"
    schema = ForumSchema
    security = ClassSecurityInfo()
    
    categories = atapi.ATFieldProperty('categories')
    category = atapi.ATFieldProperty('category')
    allow_anonymous = atapi.ATFieldProperty('allow_anonymous')
    allow_addtopic = atapi.ATFieldProperty('allow_addtopic')


    security.declarePublic('getAvaliableCategories')
    def getAvaliableCategories(self):
        parent = self.getParentNode()
        avaliable_categories = [_(u'no_category', default=u'No category'),]
        if parent.portal_type == 'Forum':
  	    for category in parent.categories:
	        avaliable_categories.append(category.decode('utf-8'))
        return avaliable_categories

atapi.registerType(Forum, PROJECTNAME)


