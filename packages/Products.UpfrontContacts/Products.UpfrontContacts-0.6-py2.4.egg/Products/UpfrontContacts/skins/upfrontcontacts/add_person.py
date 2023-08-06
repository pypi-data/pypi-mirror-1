##parameters=organisation_uid

""" Create a person and set it's organisation
"""
from Products.CMFCore.utils import getToolByName

person_id = context.generateUniqueId('Person')

# set organisation on session as reference
session = None
sdm = getToolByName(context, 'session_data_manager', None)
if sdm is not None:
    session = sdm.getSessionData(create=0)
    if session is None:
        session = sdm.getSessionData(create=1)
session.set(person_id, {'Organisation': organisation_uid})

# Create and redirect to person
person = context.restrictedTraverse('portal_factory/Person/' + person_id)
context.REQUEST.RESPONSE.redirect('%s/edit' % person.absolute_url())
