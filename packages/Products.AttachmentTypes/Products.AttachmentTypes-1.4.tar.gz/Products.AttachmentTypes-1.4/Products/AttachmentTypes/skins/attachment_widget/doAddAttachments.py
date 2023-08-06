## Controller Python Script "doAddAttachments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=attachmentFiles=None
##title=Upload new attachments
##

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

request = context.REQUEST
id = request.get('id', context.getId())

plone_utils = getToolByName(context, 'plone_utils')

def findUniqueId(id):
    contextIds = context.objectIds()

    if id not in contextIds:
        return id

    dotDelimited = id.split('.')

    ext = dotDelimited[-1]
    name = '.'.join(dotDelimited[:-1])

    idx = 0
    while(name + '.' + str(idx) + '.' + ext) in contextIds:
        idx=+1

    return(name + '.' + str(idx) + '.' + ext)


# Move object out of portal factory if necessary. We can't create images inside
# a folder in the portal factory
new_context = context.portal_factory.doCreate(context, id)

status = 'failure'
message = _("You must select an attachment to upload")

if attachmentFiles:
    for attachmentFile in attachmentFiles:
        if attachmentFile['file']:
            # Make sure we have a unique file name
            file = attachmentFile['file']
            fileName = file.filename
            title = attachmentFile['title']

            imageId = ''

            if fileName:
                fileName = fileName.split('/')[-1]
                fileName = fileName.split('\\')[-1]
                fileName = fileName.split(':')[-1]

                imageId = plone_utils.normalizeString(fileName)

            if not imageId:
                imageId = plone_utils.normalizeString(title)

            imageId = findUniqueId(imageId)

            newImageId = new_context.invokeFactory(id = imageId, type_name = 'FileAttachment')
            if newImageId is not None and newImageId != '':
                imageId = newImageId

            object = getattr(new_context, imageId, None)
            object.setTitle(title)
            object.setFile(file)
            object.reindexObject()

            status = 'success'
            message = _("Attachment(s) added")

return status, message, new_context