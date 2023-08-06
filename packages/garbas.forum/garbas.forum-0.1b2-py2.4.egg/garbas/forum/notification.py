
from Acquisition import aq_inner

from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName

from garbas.forum.interfaces import IForumNotification


NOTIFICATION_KEY = 'garbas.forum.notification'

class ForumNotification(object):
    """ notification """

    implements(IForumNotification)

    def __init__(self, context):
        self.context = aq_inner(context)
        self.annotations = IAnnotations(self.context)
        notifications = self.annotations.get(NOTIFICATION_KEY, None)
        if notifications is None:
            self.annotations[NOTIFICATION_KEY] = PersistentList()

    def notification_emails(self, ignore=[]):
        notification_list = []
        membership = getToolByName(self.context, 'portal_membership')
        for member in self.annotations[NOTIFICATION_KEY]:
            if member not in ignore:
                member = membership.getMemberById(member)
                if member:
                    member_email = member.getProperty('email')
                    if member_email:
                        notification_list.append(member_email)
        return notification_list

    def subscribe(self, member):
        if member not in self.annotations[NOTIFICATION_KEY]:
            if member:
                self.annotations[NOTIFICATION_KEY].append(member)
    
    def unsubscribe(self, member):
        if member in self.annotations[NOTIFICATION_KEY]:
            self.annotations[NOTIFICATION_KEY].remove(member)



