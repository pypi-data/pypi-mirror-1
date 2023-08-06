cur_path = '/'.join(context.getPhysicalPath())

# query for all organisations instances
organisations = context.portal_catalog(path=cur_path,
    portal_type='Organisation', sort_on='sortable_title')

# query for all people instances
people = context.portal_catalog(path=cur_path, portal_type='Person',
    sort_on='sortable_title')

# build a list of lists
result = []
for organisation in organisations:
    r = []
    r.append(organisation)
    for person in people:
        if person.getOrganisationUID == organisation.UID:
            r.append(person)
    result.append(r)

return result
