## Controller Python Script "widget_attachmentsmanager_upload"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Upload a new attachment
##

from Products.CMFCore.utils import getToolByName

request = context.REQUEST
id = request.get('id', context.getId())
attachmentTitle = request.get('attachmentTitle', None)
attachmentFile = request.get('attachmentFile', None)

# Move object out of portal factory if necessary. We can't create images inside
# a folder in the portal factory
new_context = context.portal_factory.doCreate(context, id)

status  = 'failure'
message = "You must select an attachment to upload"


if attachmentFile and context.portal_type == 'Normativa':

    prefix = "_".join( ( context.getAbbreviation(),
                         str(context.getNumber()),
                         str(context.getDate().year()) ) )

    contextIds = context.objectIds()
    contextIds.append(context.getFile().filename)

    dotDelimited = attachmentFile.filename.split('.')
    idx = 0

    if len(dotDelimited) > 1:
        ext = dotDelimited[-1]
        if not attachmentTitle:
            attachmentTitle = ".".join(dotDelimited[:-1])

        fileId = prefix + '.' + ext
        while fileId in contextIds:
            idx   += 1
            fileId = prefix + '_' + str(idx) + '.' + ext

    else:
        if not attachmentTitle:
            attachmentTitle = attachmentFile.filename

        fileId = prefix
        while fileId in contextIds:
            idx   += 1
            fileId = prefix + '_' + str(idx)

    #esto no se puede hacer en un python script, necesito hacerlo en un evento
    #attachmentFile.filename = object.id

    newfileId = new_context.invokeFactory(id = fileId, type_name = 'Attachment', file=attachmentFile, title=attachmentTitle)
    object    = getattr(new_context, newfileId, None)
    object.reindexObject()
    status  = 'uploaded'
    message = "Attachment added"

# Because we may have brough an object out of the portal_factory, we need
# to fiddle the action manually here

templateName = request['PATH_INFO'].split('/')[-1]
targetPath = '/'.join(new_context.getPhysicalPath()) + '/' + templateName

return state.set(context = new_context,
                  status = status,
                  portal_status_message = message,
                  next_action = 'traverse_to:string:%s' % targetPath)
