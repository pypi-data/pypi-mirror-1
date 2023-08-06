from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin

schema = BaseBTreeFolderSchema.copy()

class ContactManager(BrowserDefaultMixin, BaseBTreeFolder):
    """ Manage companies and people """
    security = ClassSecurityInfo()
    portal_type = meta_type = 'ContactManager' 
    archetype_name = 'Contact Manager'
    schema = schema
    allowed_content_types = ()
    content_icon = 'contactmanager.png'
    immediate_view = 'contactmanager_view'
    default_view = 'contactmanager_view'
    global_allow = 1
    filter_content_types = 0
    _at_rename_after_creation = True
    __implements__ = (BaseFolder.__implements__ + 
                     BrowserDefaultMixin.__implements__)

    actions = (
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/contactmanager_view',
         'permissions': (permissions.View,),
        },
    )

registerType(ContactManager)
