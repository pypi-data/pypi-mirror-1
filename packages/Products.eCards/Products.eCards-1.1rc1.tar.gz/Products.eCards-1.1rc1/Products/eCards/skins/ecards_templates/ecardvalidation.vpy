## Script (Python) "eCardValidation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
# validate required variables here

from Products.CMFPlone import PloneMessageFactory as _
plone_utils=context.plone_utils

# Acquire form variables
sender_first_name      = context.REQUEST.get('sender_first_name', None)
sender_last_name       = context.REQUEST.get('sender_last_name', None)
send_from_address      = context.REQUEST.get('send_from_address', None)
friend_first_name      = context.REQUEST.get('friend_first_name', None)
friend_last_name       = context.REQUEST.get('friend_last_name', None)
send_to_address        = context.REQUEST.get('send_to_address', None)
comment                = context.REQUEST.get('comment', None)

if not sender_first_name:
   state.setError('sender_first_name', _(u'Please enter your first name'))

if not sender_last_name:
   state.setError('sender_last_name', _(u'Please enter your last name'))

if not send_from_address:
   state.setError('send_from_address', _(u'Please enter your email address'), 'email_required')
elif not plone_utils.validateEmailAddresses(send_from_address):
   state.setError('send_from_address', _(u"""Your email address doesn't seem valid.  Please re-enter it."""))

if not friend_first_name:
   state.setError('friend_first_name', _(u"""Please enter your friend's first name"""))

if not friend_last_name:
   state.setError('friend_last_name', _(u"""Please enter your friend's last name"""))

if not send_to_address:
   state.setError('send_to_address', _(u"""Please enter your friend's email"""), 'email_required')
elif not plone_utils.validateEmailAddresses(send_to_address):
   state.setError('send_to_address', _(u"""Your friend's email address doesn't seem valid.  Please re-enter it."""))

if not comment:
   state.setError('comment', _(u'Please enter a message for your friend'))

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure')
else:
    return state

