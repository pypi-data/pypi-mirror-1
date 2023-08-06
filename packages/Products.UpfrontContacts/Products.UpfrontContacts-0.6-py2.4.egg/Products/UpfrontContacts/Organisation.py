from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.UpfrontContacts.organisation_schema import schema
from Products.UpfrontContacts.interfaces import IOrganisation

class Organisation(BaseFolder):
    """ Organisation
    """
    security = ClassSecurityInfo()
    portal_type = meta_type = 'Organisation' 
    archetype_name = 'Organisation'
    schema = schema
    allowed_content_types = ()
    content_icon = 'organisation.png'
    immediate_view = 'base_view'
    global_allow = 1
    filter_content_types = 0
    _at_rename_after_creation = True

    actions = ()

    def manage_beforeDelete(self, item, container):
        """ Delete referenced contacts if we are in the context of a
            ContactManager.
        """
        if self.aq_parent.meta_type == 'ContactManager':
            for contact in self.getContacts():
                parent = contact.aq_inner.aq_parent
                parent.manage_delObjects(contact.getId())
        BaseFolder.manage_beforeDelete(self, item, container)


    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    security.declareProtected(permissions.View,
        'getPhysicalAddressAsString')
    def getPhysicalAddressAsString(self):
        """ Return Physical Address as string
        """
        field = self.Schema().get('PhysicalAddress')
        subfieldViews = field.getSubfieldViews(self, field.innerJoin)
        return ', '.join(subfieldViews)


registerType(Organisation)
