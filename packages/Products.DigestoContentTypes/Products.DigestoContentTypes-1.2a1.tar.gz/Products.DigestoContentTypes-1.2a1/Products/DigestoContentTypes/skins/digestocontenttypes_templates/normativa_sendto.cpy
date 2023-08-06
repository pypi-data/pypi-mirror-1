## Controller Python Script "normativa_sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=addressbook=[], normativas=[]
##title=Send a list of Normativas with an optional comment to a list of emails from the address book
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')
site_properties = getToolByName(context, 'portal_properties').site_properties
pretty_title_or_id = plone_utils.pretty_title_or_id

if not mtool.checkPermission(AllowSendto, context):
    context.plone_utils.addPortalMessage(_(u'You are not allowed to send this link.'))
    return state.set(status='failure')

at = getToolByName(context, 'portal_actions')
show = False
actions = at.listActionInfos(object=context)
# Check for visbility of sendto action
for action in actions:
    if action['id'] == 'sendto' and action['category'] == 'document_actions':
        show = True
if not show:
    context.plone_utils.addPortalMessage(_(u'You are not allowed to send this link.'))
    return state.set(status='failure')


send_from_address = REQUEST.send_from_address
send_to_address = ";".join(addressbook)
subject = REQUEST.get('subject', 'Notificación de Normativas')
envelope_from = site_properties.email_from_address

url = context.absolute_url()

normativas_text = ""
if normativas:
    normativas_text += "\n\n".join(normativas)

comment = REQUEST.get('comment', None)


try:
    portal = getToolByName(context, 'portal_url').getPortalObject()
    host = getattr(portal, 'MailHost')
    encoding = portal.getProperty('email_charset')

    template = getattr(context, 'normativa_sendto_template')

    text = template(context,
                    send_to_address=send_to_address,
                    send_from_address=send_from_address,
                    comment=comment,
                    subject=subject,
                    normativas = normativas_text)


    result = host.secureSend(text, send_to_address, envelope_from,
                             subject=subject, subtype='plain', charset=encoding,
                             debug=False, From=send_from_address)
except ConflictError:
    raise
except: # TODO To many things could possibly go wrong. So we catch all.
    exception = context.plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    context.plone_utils.addPortalMessage(message)
    return state.set(status='failure')
#REQUEST.send_to_address
tmsg='Sent page %s to %s' % (url, send_to_address)
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
