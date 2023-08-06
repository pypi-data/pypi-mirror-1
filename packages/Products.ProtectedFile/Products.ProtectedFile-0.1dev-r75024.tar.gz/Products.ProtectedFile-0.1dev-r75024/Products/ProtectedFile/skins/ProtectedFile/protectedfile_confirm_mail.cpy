## Controller Python Script "send_confirm_email_for_protectedfile"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=
##

# The email is already validated to be of an ok format at least
email = context.REQUEST.get('emailaddress')

# Call the protectedfile to write the email to the mapping
# and get the code in return
key = context.addToken(email)

# Send an email to the supplied address, including the code
context.sendFileAddressMail(email, key)

# Always make sure to return the ControllerState object
return state
