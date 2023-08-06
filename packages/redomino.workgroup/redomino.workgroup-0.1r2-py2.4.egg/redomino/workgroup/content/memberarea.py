# TODO: this code needs to be fixed!!

from zope.interface import alsoProvides

from Products.Archetypes.public import *
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATBTreeFolderSchema
from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.CMFCore.utils import getToolByName

from redomino.workgroup.config import PROJECTNAME

memberarea_schema = ATBTreeFolderSchema.copy() + Schema ((

))

class MemberArea(ATBTreeFolder):

    security = ClassSecurityInfo()

    schema         = memberarea_schema
#    content_icon   = 'folder_icon.gif'
    meta_type      = 'MemberArea'
    portal_type    = 'MemberArea'
    archetype_name = 'MemberArea'
    global_allow = 1
    allowed_content_types = ['Member']
    filter_content_types = 1
#    default_view   = 'folder_listing'
#    immediate_view = 'folder_listing'

registerType(MemberArea, PROJECTNAME)
