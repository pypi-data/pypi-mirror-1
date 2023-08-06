import base64
import csv
from cStringIO import StringIO
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject
from Products.UpfrontContacts.person_schema import person_schema
from Products.UpfrontContacts.organisation_schema import \
    schema as organisation_schema
from config import CSV_KEY
import transaction

class UpfrontContactsTool(UniqueObject, SimpleItem):
    """ Upfront Contacts Tool.
    """

    id = 'upfront_contacts_tool'
    meta_type = 'Upfront Contacts Tool'

    security = ClassSecurityInfo()
    security.declareObjectProtected(permissions.View)


    def _del_session_cache(self):
        ses = self.REQUEST.SESSION
        if ses.has_key(CSV_KEY):
            del ses[CSV_KEY]


    security.declareProtected(permissions.View,
        'uploadCSVFile')
    def uploadCSVFile(self, REQUEST=None):
        """
        Read uploaded csv file and save it in sessions variable
        """
        session = self.REQUEST.SESSION
        csv_file = self.REQUEST.get('csv_file', None)
        if csv_file is None:
            self._del_session_cache()
        else:
            session[CSV_KEY] = csv_file.read()

        if REQUEST:
            url = self.REQUEST.get('current_url', self.absolute_url())
            self.REQUEST.RESPONSE.redirect(
                '%s/uc_import_contacts_format' % url)


    def _site_encoding(self):
        "Returns the site encoding"
        portal_properties = self.portal_properties
        site_props = portal_properties.site_properties
        return site_props.default_charset or 'utf-8'


    security.declareProtected(permissions.View,
                              'csv_parser')
    def csv_parser(self, delimiter='comma', quote_char='double_quote',
                   coding='latin-1'):
        """Don't import HectoMegaByte files, or you are asking for it!"""
        delim_map = {'tab':'\t', 'semicolon':';', 'colon':':', 'comma':',', 'space':' ', }
        delimiter = delim_map[delimiter]
        quote_map = {'double_quote':'"', 'single_quote':"'", }
        quote_char = quote_map[quote_char]
        charset = self._site_encoding()
        csv_file_content = self.REQUEST.SESSION.get(CSV_KEY, '')

        # Horrid workaround to get the buffer in U (universal line terminator) mode
        from tempfile import mkstemp
        from os import close, write, system
        # Write temp file
        fp, fname = mkstemp()
        try:
            write(fp, csv_file_content)
        finally:
            close(fp)
        # Read temp file
        fh = open(fname, 'rU')
        try:
            buf = fh.read()
        finally:
            fh.close()
            system('rm "%s"' % fname)

        # this sucks! double memory usage
        f = StringIO(buf.decode(coding, 'replace').encode(charset))
        reader = csv.reader(f, delimiter=delimiter, lineterminator=chr(13))
        rows = []
        for row in reader:
            rows.append(row)
        return rows


    security.declareProtected(permissions.View,
                              'contactTypeFieldNames')
    def contactTypeFieldNames(self, import_type):
        "Returns the field names for contact type"
        if import_type == 'Person':
            schema = person_schema
        elif import_type == 'Organisation':
            schema = organisation_schema
        fields = schema.filterFields(isMetadata=0)
        field_names = []
        for field in fields:
            if field.type in ('string', 'text', 'date', 'boolean', 'integer', 'datetime'):
                field_names.append(field.getName()) 
            elif field.type == 'address':
                for key in field.subfields:
                    field_names.append(
                        '%s.%s' % (field.getName(), key)
                    )
        return field_names


    def _getFieldsMap(self, REQUEST):
        "Returns the fields map from the request"
        fields_map = {}
        n_fields = REQUEST.get('n_fields', 0)
        for n in range(n_fields):
            fieldname = REQUEST.get('fields_map_%s' % n, '')
            if fieldname != '*discard*':
                fields_map.setdefault(fieldname, []).append(n)
        return fields_map


    def _field_types(self, import_type):
        "Returns a dict with mapping of field and its type"
        if import_type == 'Person':
            schema = person_schema
        elif import_type == 'Organisation':
            schema = organisation_schema
        fields = schema.filterFields(isMetadata=0)
        field_types = {}
        for field in fields:
            field_types[field.getName()] = field.type
        return field_types


    def _unique(self, dicts):
        "Removes duplicates from the import map."
        uniques = {}
        for dict_ in dicts:
            keys = dict_.keys()
            keys.sort()
            temp = []
            for key in keys:
                # stringify value in case we have an unhashable type
                val = str(dict_[key])
                temp.append((key, val))
            uniques[tuple(temp)] = dict_
        vals = uniques.values()
        return vals


    def _addContacts(self, container, import_type, import_maps, REQUEST=None):
        "Add contacts to self."
        import_maps = self._unique(import_maps)
        now = self.ZopeTime()
        d_time = now.strftime('%Y%m%dZ%H%M%S')
        l_import_type = import_type.lower()
        id_prefix = '%s.%s.%%s' % (l_import_type, d_time)
        
        number_to_add = len(xrange(len(import_maps)))
        if REQUEST is not None:
            progress = self.uc_import_progress(REQUEST=REQUEST)
            REQUEST.RESPONSE.write(progress.encode(self._site_encoding()))
            REQUEST.RESPONSE.write('<input style="display: none;" id="inputTotal" value="%s">' % number_to_add)
        
        for i in xrange(len(import_maps)):
            import_map = import_maps[i]
            # we pop the id instead of getting it so the iteration below
            # does not not try to set it again.
            id = import_map.pop('id', id_prefix % i)
            container.invokeFactory(import_type, id)
            obj = container._getOb(id)
            for key, val in import_map.items():
                obj.Schema().getField(key).set(obj, val)
            obj.reindexObject()
            # if more objects are imported than can be held in the cache
            # it slows down. So we do partial commits for every 200 objects
            if i and not i % 200:
                transaction.commit()

            # Output progress
            if ((i+1) % 50 == 0) and (REQUEST is not None):
                REQUEST.RESPONSE.write('<input style="display: none;" name="inputProgress" value="%s">' % (i+1))

        transaction.commit()


    security.declareProtected(permissions.View,
                              'importCSV')
    def importCSV(self, delimiter='comma', quote_char='double_quote', 
                  coding='utf-8', import_type=None, link_via_title=0, 
                  REQUEST=None):
        "Convert the uploaded csv data to contact types"
        fields_map = self._getFieldsMap(REQUEST)
        delimiter_map = {'string':' ','text':'\n'}
        field_types = self._field_types(import_type)
        rows = self.csv_parser(delimiter, quote_char, coding)
        # get the data from the fields and put them in dict of
        # {attrname:value}
        import_maps = []
        errors = []
        row_idx = 1
        for row in rows:
            errorflag = 0
            import_map = {}
            for key, val in fields_map.items():
                if key.find('.') != -1:
                    key, subkey = key.split('.')
                field_type = field_types[key]
                delimiter = delimiter_map.get(field_type, ' ')
                
                vals = []
                # find the values
                row_len = len(row)
                for v in val:
                    if (v < row_len) and row[v]:
                        if field_type == 'boolean':
                            # Convert string into '1' (True) or '' (False).
                            # The value must be a string since it is an argument to join() later in this method.
                            elem = row[v]
                            b = (type(elem) is type('string')) and \
                                (elem.lower() in ('true','yes','t','y') and '1') or \
                                (elem.lower() in ('false','no','f','n') and '')
                                
                            # Any values other than those in the expression above (y,n etc) will return False. Detect this and abort.
                            if b is False: 
                                errors.append({'msg':"Row %s contains an invalid boolean value (%s)" % (row_idx, elem), 'row':','.join(row)})
                                errorflag = 1
                            
                            vals.append(b)
                            
                        elif field_type == 'integer':                         
                            try:
                                i = int(row[v])
                            except:
                                errors.append({'msg':"Row %s contains an invalid integer value (%s)" % (row_idx, row[v]), 'row':','.join(row)})
                                errorflag = 1
                                
                            vals.append(str(i))
                            
                        elif field_type == 'datetime':                         
                            from DateTime import DateTime
                            try:
                                d = DateTime(row[v])
                            except:
                                errors.append({'msg':"Row %s contains an invalid datetime value (%s)" % (row_idx, row[v]), 'row':','.join(row)})
                                errorflag = 1
                                
                            vals.append(str(d))

                        else:
                            vals.append(row[v])
                    else:
                        vals.append('')
                
                if not errorflag:
                    if field_type == 'address':
                        d = import_map.get(key, {})
                        d[subkey] = delimiter.join(vals)
                        import_map[key] = d
                    else:
                        import_map[key] = delimiter.join(vals)
                        
            if not errorflag:                        
                import_maps.append(import_map)

            row_idx += 1
           
        # Errors?
        if len(errors) > 0:
            container = self.unrestrictedTraverse(
                self.REQUEST.get('current_path'))
            return container.uc_import_error(REQUEST=REQUEST, errors=errors)

        # add the contacts
        container = self.unrestrictedTraverse(
            self.REQUEST.get('current_path'))
        self._addContacts(container, import_type, import_maps, REQUEST)
        # delete file from session object as it can be several MB
        self._del_session_cache()

        # if link_via_title is true, we must relate organizations to
        # persons via the organizations title. Often contacts are
        # imported from flat tables, so this can be the most practical
        # way to do it.

        if link_via_title:
            org_titles = {} # map organization titles to organisations
            for org in self.contentValues(
                    filter={'portal_type':'Organisation'}):
                org_titles.setdefault(org.Title(), []).append(org)

            person_titles = {}
            for person in self.contentValues(
                    filter={'portal_type':'Person'}):
                if person.getOrganizationName() and (
                        not person.getOrganization()):
                    person_titles.setdefault(person.getOrganizationName(),
                                             []).append(person)

            for org_title, persons in person_titles.items():
                for person in persons:
                    orgs = org_titles.get(org_title, [])
                    for org in orgs:
                        person.addReference(org.UID(), EMPLOYED_REF)

        if REQUEST:
            # This trick is needed since previous calls to RESPONSE.write trashes a normal redirect
            REQUEST.RESPONSE.write('<script>document.location.href="%s?portal_status_message=Import%%20succeeded"</script>' % container.absolute_url())

    security.declareProtected(permissions.View, 'exportCSV')
    def exportCSV(self, contacts=None, fields=None, delimiter='comma', 
                  quote_char='double_quote', coding='latin-1',
                  export_type='Person'):

        """
        Exports a list of contacts as a CSV file.
        contacts: if None it exports all contact persons in the folder.
        fields: field names to export
        """
        container = self.unrestrictedTraverse(
            self.REQUEST.get('current_path'))
        if contacts is None:
            contacts = container.listFolderContents(
                contentFilter={'portal_type':export_type}
            )

        delim_map = {
            'tabulator':'\t',
            'semicolon':';',
            'colon':':',
            'comma':',',
            'space':' ',
        }

        delimiter = delim_map[delimiter]
        quote_map = {'double_quote':'"', 'single_quote':"'", }
        quote_char = quote_map[quote_char]
        
        # generate result
        if fields is None:
            result = ''
        else:
            rows = [fields]
            for contact in contacts:
                row = []
                for fieldname in fields:
                    if fieldname.find('.') != -1:
                        fieldname, key = fieldname.split('.')

                    field = contact.Schema()[fieldname]
                    value = getattr(contact, field.accessor)()

                    if field.type == 'address':
                        value = value.get(key, '')
                    elif field.type == 'boolean':
                        if value is None:
                            value = ''
                        elif value is True:
                            value = 'True'
                        elif value is False:
                            value = 'False'
                        else:
                            value = ''
                    elif field.type == 'datetime':
                        if value is None:
                            value = ''
                        else:
                            value = str(value)
                    elif field.type == 'integer':
                        if value is None:
                            value = ''
                        else:
                            value = str(value)
                    elif field.type == 'reference':
                        if value:
                            if isinstance(value, ListType):
                                value = ', '.join(
                                    [v.title_or_id() for v in value]
                                    )
                            else:
                                value = value.title_or_id()
                        else:
                            value = ''                            
                    value = str(value)
                    if value.find('\r\n') != -1:
                        value.replace('\r\n', '\n')
                    row.append(value)
                rows.append(row)
            # convert lists to csv string
            ramdisk = StringIO()
            writer = csv.writer(ramdisk, delimiter=delimiter)
            writer.writerows(rows)
            result = ramdisk.getvalue()
            ramdisk.close()

        # encode the result
        charset = self._site_encoding()
        if coding:
            result = result.decode(charset).encode(coding)
        else:
            coding = charset

        # set headers and return
        setheader = self.REQUEST.RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type', 
            'text/x-comma-separated-values; charset=%s' % coding)
        setheader('Content-Disposition', 'filename=%s.csv' % self.getId())
        return result


    security.declareProtected(permissions.View, 'import_vCard')
    def import_vCard(self, REQUEST=None):
        """Import VCARD as person in current folder
        """
        container = self.unrestrictedTraverse(
            self.REQUEST.get('current_path'))

        vcard_file = REQUEST.get('vcard_file', None)
        if vcard_file is not None:
            vcard = vcard_file.read()

        values = self.parse_vcard(vcard)

        new_id = self.generateUniqueId('Person')
        container.invokeFactory(id=new_id, type_name='Person')
        person = container._getOb(new_id)
        for field_id, value in values.items():
            field = person.Schema()[field_id]
            mutator = field.getMutator(person)
            mutator(value)

        person._renameAfterCreation(check_auto_id=True)
        person.at_post_create_script()

        if REQUEST:
            REQUEST.RESPONSE.redirect(person.absolute_url())

    security.declareProtected(permissions.View, 'base64encode')
    def base64encode(self, s):
        """ Encode a string in base64
        """
        return base64.encodestring(s)

    security.declareProtected(permissions.View, 'base64decode')
    def base64decode(self, s):
        """ Decode a base64 encode string
        """
        return base64.decodestring(s)

InitializeClass(UpfrontContactsTool)
