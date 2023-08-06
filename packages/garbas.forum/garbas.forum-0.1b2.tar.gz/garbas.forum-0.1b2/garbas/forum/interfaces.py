
from zope.interface import Interface


class IForum(Interface):
    """forum content"""

class IForumTopic(Interface):
    """forum topic content"""

class IForumPost(Interface):
    """forum post content"""

class IForumNotifiable(Interface):
    """ forum notifiable """

class IForumNotification(Interface):
    """ forim notification """

