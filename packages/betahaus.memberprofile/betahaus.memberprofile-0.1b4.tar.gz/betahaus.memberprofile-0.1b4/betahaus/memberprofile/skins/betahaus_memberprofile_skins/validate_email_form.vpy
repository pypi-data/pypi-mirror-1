## Controller Script Python "validate_email_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=sender_email,sender_fullname
##title=validates the form for sending email messages

# cannot be calles _ it will be picked up by i18ndude
from Products.CMFPlone import PloneMessageFactory as pmf
reg_tool=context.portal_registration 

if not sender_email:
    state.setError('sender_email', pmf(u'Please submit an email address.'), 'sender_email_required')
else:
    if not reg_tool.isValidEmail(sender_email):
        state.setError('sender_email', pmf(u'You entered an invalid email address.'), 'invalid_email')
 
if not (sender_fullname and sender_fullname.strip()):
    state.setError('sender_fullname', pmf(u'Please enter a full name.'), 'sender_fullname_required')

#if not (message and message.strip()):
#    state.setError('message', _(u'Please enter a message'), 'message_required')

#if not (text and text.strip()):
#    state.setError('text', _(u'Enter a message'), 'text_required')


if state.getErrors():
    context.plone_utils.addPortalMessage(pmf(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
