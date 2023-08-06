
from Products.CMFCore.permissions import setDefaultRoles

SubmitNewPost = "Forum: Submit New Post"

def initialize_permissions():
    setDefaultRoles(SubmitNewPost, ['Manager',])

