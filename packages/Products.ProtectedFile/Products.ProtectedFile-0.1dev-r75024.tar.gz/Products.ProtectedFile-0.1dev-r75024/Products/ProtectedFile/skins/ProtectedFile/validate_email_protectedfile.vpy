## Controller Validator "validate_email_protectedfile"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=emailaddress=None
##title=
##

if not emailaddress:
   state.setError('emailaddress', 'Please enter a valid email address')
else:
    reg_tool = context.portal_registration
    if not reg_tool.isValidEmail(emailaddress):
        state.setError('emailaddress', 'Please enter a valid email address')

if state.getErrors():
   # An error has occurred.  Set the status to 'failure'
   # (the default initial status is 'success')
   state.setStatus('failure')
   # Return the state and pass the variable portal_status_message in the REQUEST
   return state.set(portal_status_message='Please correct the errors shown')

# No errors. Always make sure to return the ControllerState object
return state
