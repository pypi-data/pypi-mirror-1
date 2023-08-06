## Script (Python) "validate_integrity"
##title=Validate Integrity
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##
errors = {}
errors = context.validate(REQUEST=context.REQUEST, errors=errors, data=1, metadata=0)

if errors:
    return state.set(status='failure', errors=errors, portal_status_message='Please correct the indicated errors.')
else:
    # redirect to parent if we are in the context of a ContactManager
    if context.aq_parent.portal_type == 'ContactManager':
        status = 'success_contacts'
    else:
        status = 'success'
    return state.set(status=status, portal_status_message='Changes saved.')
