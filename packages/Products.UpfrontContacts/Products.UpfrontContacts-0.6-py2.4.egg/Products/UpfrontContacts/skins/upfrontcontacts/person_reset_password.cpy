## Controller Python Script "person_reset_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=username
##title=Reset user password
##
member = context.portal_membership.getMemberById(username)
pw = context.portal_registration.generatePassword()
context.acl_users.userFolderUpdateUser(username, password=pw)
if pw:
    context.REQUEST.form['new_password'] = pw
    context.portal_registration.mailPassword(username, context.REQUEST)

return state.set(portal_status_message=context.translate('Password reset.'))
