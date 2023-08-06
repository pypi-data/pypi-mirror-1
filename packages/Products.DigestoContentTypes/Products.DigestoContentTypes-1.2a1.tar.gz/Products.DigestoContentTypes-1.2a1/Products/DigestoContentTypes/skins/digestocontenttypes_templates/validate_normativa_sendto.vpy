## Controller Script Python "validate_sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=addressbook=[],normativas=[],send_from_address='',subject=''
##title=validates the email adresses

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _
plone_utils=context.plone_utils

if not addressbook:
    state.setError('addressbook', _(u'Please select at least one e-mail destination.'), 'email_required')

if not normativas:
    state.setError('normativas', _(u'Please select at least one normativa to send.'), 'normativa_required')

if not send_from_address:
    state.setError('send_from_address', _(u'Please submit an email address.'), 'email_required')

if not subject:
    state.setError('subject', _(u'Please submit a subject.'), 'subject_required')

if not plone_utils.validateSingleEmailAddress(send_from_address):
    state.setError('send_from_address', _(u'Please submit a valid email address.'), 'email_required')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure')
else:
    return state
