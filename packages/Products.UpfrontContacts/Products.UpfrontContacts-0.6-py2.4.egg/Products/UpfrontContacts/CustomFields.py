from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import DisplayList, ObjectField
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.ATExtensions.Extensions.utils import makeDisplayList

from Products.validation.validators.RegexValidator import RegexValidator
from Products.validation import validation
validation.register(
    RegexValidator('isNumber', r'^([+-])?[0-9 ]+$', title='XXX',
                    description='XXX', errmsg='is not a valid number.')
)

def getValues(self, prop_name):
    ptool = getToolByName(self, 'portal_properties', None)
    if ptool and hasattr(ptool, 'upfrontcontacts_properties'):
        return ptool.upfrontcontacts_properties.getProperty(prop_name, None)
    else:
        return None
    
def getDisplayList(self, prop_name=None):
    return makeDisplayList(getValues(self, prop_name))


class FixRecordFieldMixin:
    """ RecordField does not cope with uninitialized field on an
        instance
    """
    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        if value:
            return self._encode_strings(value, instance, **kwargs)
        else:
            return {}


class AddressField(FixRecordFieldMixin, RecordField):
    """ dedicated address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'address',
        'subfields' : ('address', 'city', 'zip', 'state', 'country'),
        'subfield_labels':{'zip':'Postal code'},
        'subfield_vocabularies' :{'country':'CountryNames'},
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()
    
    security.declarePublic("CountryNames")
    def CountryNames(self, instance=None):
        if not instance:
            instance = self
        return getDisplayList(instance, 'country_names')


registerField(AddressField,
              title="Address",
              description="Used for storing address information",
              )

