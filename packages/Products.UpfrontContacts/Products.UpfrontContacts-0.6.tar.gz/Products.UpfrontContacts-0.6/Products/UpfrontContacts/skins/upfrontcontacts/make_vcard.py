## Python Script "make_vcard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contact=None
##title=Return a vcard for a contact
##
""" Customise this method if you add fields to your Person schema that
    you want to see in vCard exports.
"""
if contact is None:
    contact = context

vcard = [
    "BEGIN:VCARD",
    "VERSION:3.0",
]

def wrap(value):
    # When generating a content line, lines longer than 75
    # characters SHOULD be folded according to the folding
    # described in http://www.faqs.org/rfcs/rfc2426.html
    s = ''
    while value:
        s += value[:75] + "\r\n "
        value = value[75:]
    # remove last CRLF and space
    s = s[:-3]
    return s

def addvalue(key, value):
    # helper method to skip empty values, escape commas and
    # semicolons and format line breaks. See
    # http://www.faqs.org/rfcs/rfc2426.html

    # A formatted text line break in a text value type MUST be
    # represented as the character sequence backslash (ASCII decimal 92)
    # followed by a Latin small letter n (ASCII decimal 110) or a Latin
    # capital letter N (ASCII decimal 78), that is "\n" or "\N".

    if not value:
        return 

    if 'ENCODING=b' in key:
        # join lines so that we can rewrap them
        value = value.replace('\n', '')
    else:
        if same_type(value, ""):
            value = [value]

        l = []
        for v in value:
            v = v.replace(",", "\,")
            v = v.replace(";", "\;")
            v = v.replace("\r\n", "\\n")
            v = v.replace("\n", "\\n")
            l.append(v)
        value = ";".join(l)

    value = "%s:%s" % (key, value)
    if len(value) > 75:
        value = wrap(value)

    vcard.append( value )


addvalue( "FN", contact.getFullname() )
addvalue( "N", (contact.getLastName(),
                contact.getFirstName(),
                "", # additional name not in default schema
                "" # salutation not in default schema
                )
        )
photo = contact.getPortrait()
if photo:
    img = photo.data
    img_type = photo.getContentType().split('/')[1]
    img_encoded = context.upfront_contacts_tool.base64encode(img)
    key = "PHOTO;ENCODING=b;TYPE=%s" % img_type
    addvalue(key, img_encoded)
        

birthdate = contact.getBirthDate()
if birthdate:
    addvalue( "BDAY", birthdate.ISO8601() )

street = contact.getPhysicalAddress()
if street:
    addvalue( "ADR;TYPE=home", (
                    "",
                    "", # extended address not in default schema
                    street.get('address', ''),
                    street.get('city', ''),
                    street.get('state', ''),
                    street.get('zip', ''),
                    street.get('country', '')
                    )
            )

postal = contact.getPostalAddress()
if postal:
    addvalue( "ADR;TYPE=postal", (
                    "",
                    "", # extended address not in default schema
                    postal.get('address', ''),
                    postal.get('city', ''),
                    postal.get('state', ''),
                    postal.get('zip', ''),
                    postal.get('country', '')
                    )
            )
addvalue( "TEL;TYPE=work,voice", contact.getBusinessPhone() )
addvalue( "TEL;TYPE=work,fax", contact.getBusinessFax() )
addvalue( "TEL;TYPE=home,voice", contact.getHomePhone() )
addvalue( "TEL;TYPE=cell,voice", contact.getMobilePhone() )
addvalue( "EMAIL;TYPE=internet", contact.getEmail() )

organisation = contact.getOrganisation()
if organisation:
    addvalue( "ORG", organisation.Title() )

addvalue( "URL", contact.absolute_url() )

vcard.append("END:VCARD")

return "\r\n".join(vcard)
