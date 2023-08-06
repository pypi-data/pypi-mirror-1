## Controller Python Script "send_email_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send email to a user
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

##
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"

plone_utils = getToolByName(context, 'plone_utils')
urltool = getToolByName(context, 'portal_url')
membership = getToolByName(context, 'portal_membership')
portal = urltool.getPortalObject()
url = urltool()

## make these arguments?
subject = REQUEST.get('subject', '')
body = REQUEST.get('body', '')
to_user = REQUEST.get('to_user', '')
sender_fullname = REQUEST.get('sender_fullname', '')
sender_email = REQUEST.get('sender_email','')

# Get the recieveing user 
user = membership.getHomeFolder(to_user)
if not user:
	msg = 'User "%s" was not found.' % to_user
	plone_utils.addPortalMessage(_(msg))
	state.set(status=state_failure)
	return state
	
## Get the email of the receiving user.
to_email = user.getEmail()

envelope_from = sender_from_address = portal.getProperty('email_from_address')


state.set(status=state_success) ## until proven otherwise

host = context.MailHost # plone_utils.getMailHost() (is private)
encoding = portal.getProperty('email_charset')

variables = {'sender_from_address' : sender_from_address,
             'url'                 : url,
             'subject'             : subject,
             'body'		           : body,
             'sender_fullname'     : sender_fullname,
             'sender_email'        : sender_email,
             }

try:
	
    message = context.send_email_form_template(context, **variables)
    result = host.secureSend(message, 
							 to_email, 
							 sender_from_address, 
							 subject=subject, 
							 subtype='html', 
							 charset=encoding, 
							 debug=False, 
							 From="%s <%s>" % (sender_fullname, sender_from_address))

except ConflictError:
    raise
except: # TODO Too many things could possibly go wrong. So we catch all.
    exception = plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    plone_utils.addPortalMessage(message, 'error')
    return state.set(status=state_failure)

## clear request variables so form is cleared as well
REQUEST.set('body', None)
REQUEST.set('subject', None)
REQUEST.set('sender_from_address', None)
REQUEST.set('sender_fullname', None)
REQUEST.set('sender_email', None)
REQUEST.set('to_user', None)

plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
