from webdav.common import rfc1123_date
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.Field import decode
from Products.remember.content.member import FolderishMember
from Products.UpfrontContacts.person_schema import person_schema
from Products.Archetypes.Field import decode, encode

class Person(FolderishMember):
    """ Store contact, personal and login details of person
    """
    security = ClassSecurityInfo()
    archetype_name = 'Person'
    schema = person_schema
    allowed_content_types = ()
    content_icon = 'person.png'
    immediate_view = 'base_view'
    global_allow = 1
    filter_content_types = 0
    _at_rename_after_creation = True

    actions = (
        {'id': 'vcard',
         'name': 'vCard',
         'action': 'string:${object_url}/vcard_view',
         'permissions': (permissions.View, ),
         'category': 'document_actions',
        },
    )

    def getFullname(self):
        """ return Person's Fullname """
        fn = self.getFirstName()
        sn = self.getLastName()
        if fn or sn:
            value = '%s %s' % (self.getFirstName(), self.getLastName())
        else:
            value = ''
        return decode(value, self)

    Title = getFullname

    security.declareProtected(permissions.View, 'vcard_view')
    def vcard_view(self, REQUEST, RESPONSE):
        """vCard output
        """
        vcard = self.make_vcard()

        site_props = self.portal_properties.site_properties
        charset = site_props.default_charset or 'utf-8'

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Content-Length', len(vcard))
        RESPONSE.setHeader('Content-Type', 
            'text/directory; charset=%s; profile="vCard"' % charset)
        RESPONSE.setHeader('Content-Disposition',
            'attachment; filename=%s.vcf' % self.getId())

        return vcard


registerType(Person)
