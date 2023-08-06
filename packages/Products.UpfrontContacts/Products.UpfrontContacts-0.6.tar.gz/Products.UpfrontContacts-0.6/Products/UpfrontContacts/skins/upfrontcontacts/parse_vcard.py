## Python Script "parse_vcard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=vcard
##title=Parse vcard to contact schema
##
""" Customise this method if you add fields to your Person schema that
    you want to handle in vCard imports.
"""
from DateTime import DateTime

# join folded lines
vcard = vcard.replace('\r\n ', '__LINEBREAK__')
# split file on linebreaks
vcard = vcard.split('\r\n')

map = {}

for line in vcard:
    pos = line.find(':')
    key = line[:pos]
    value = line[pos+1:]
    key = key.upper()

    if key == 'N':
        names = value.split(';')
        field_ids = ('LastName', 'FirstName', '', '', '')
        for field_id, v in zip(field_ids, names):
            if not field_id: continue
            map[field_id] = v

    if key == 'BDAY':
        map['BirthDate'] = DateTime(value)

    if key.startswith('ADR'):
        # If we don't find postal in the key we treat it as physical
        if 'postal' in key:
            address_field_id = 'PhysicalAddress'
        else:
            address_field_id = 'PostalAddress'
            
        address = {}
        names = value.split(';')
        subfield_ids = ('', '', 'address', 'city', 'state', 'zip',
                        'country')
        for subfield_id, v in zip(subfield_ids, names):
            address[subfield_id] = v
        map[address_field_id] = address

    if key.startswith('TEL') and 'WORK' in key and 'VOICE' in key:
        map['BusinessPhone'] = value

    if key.startswith('TEL') and 'WORK' in key and 'FAX' in key:
        map['BusinessFax'] = value

    if key.startswith('TEL') and 'HOME' in key and 'VOICE' in key:
        map['HomePhone'] = value

    if key.startswith('TEL') and 'CELL' in key:
        map['MobilePhone'] = value

    if key.startswith('EMAIL'):
        map['Email'] = value

    if key == 'ORG':
        rs = context.portal_catalog(portal_type='Organisation',
            sortable_title=value)
        if rs:
            map['Organisation'] = rs[0].getObject()

    if key.startswith('PHOTO') and 'ENCODING=B' in key:
        content_type = ''
        for k in key.split(';'):
            if 'TYPE' in k:
                content_type = 'image/%s' % k.split('=')[1]
        value = value.replace('__LINEBREAK__', '')
        value = context.upfront_contacts_tool.base64decode(value)
        map['portrait'] = value

return map
