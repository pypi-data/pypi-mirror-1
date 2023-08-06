import copy

def make_listing_from_schema(schema, columns):
    listing = schema.copy()
    field_names = copy.copy(listing.keys())
    for key in field_names:
        if key not in columns:
            del listing[key]
    return listing


# utility methods copied from LDAPUserFolder.utils by Jens Vagelpohl
import codecs

encoding = 'latin1'

try:
    encodeLocal, decodeLocal, reader = codecs.lookup(encoding)[:3]
    encodeUTF8, decodeUTF8 = codecs.lookup('UTF-8')[:2]

    if getattr(reader, '__module__', '')  == 'encodings.utf_8':
        # Everything stays UTF-8, so we can make this cheaper
        to_utf8 = from_utf8 = str

    else:

        def from_utf8(s):
            return encodeLocal(decodeUTF8(s)[0])[0]

        def to_utf8(s):
            return encodeUTF8(decodeLocal(s)[0])[0]


except LookupError:
    raise LookupError, 'Unknown encoding "%s"' % encoding

