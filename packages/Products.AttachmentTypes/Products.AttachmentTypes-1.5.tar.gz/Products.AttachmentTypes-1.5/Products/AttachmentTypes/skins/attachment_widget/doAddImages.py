## Controller Python Script "doAddImages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=imageFiles=None
##title=Upload new images
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
message = _("You must select an image to upload")

if imageFiles:
    for imageFile in imageFiles:
        if imageFile['file']:
            # Make sure we have a unique file name
            file = imageFile['file']
            fileName = file.filename
            title = imageFile['title']

            imageId = ''

            if fileName:
                fileName = fileName.split('/')[-1]
                fileName = fileName.split('\\')[-1]
                fileName = fileName.split(':')[-1]

                imageId = plone_utils.normalizeString(fileName)

            if not imageId:
                imageId = plone_utils.normalizeString(title)

            imageId = findUniqueId(imageId)

            newImageId = new_context.invokeFactory(id = imageId, type_name = 'ImageAttachment')
            if newImageId is not None and newImageId != '':
                imageId = newImageId

            object = getattr(new_context, imageId, None)
            object.setTitle(title)
            object.setImage(file)
            object.reindexObject()
            status = 'success'
            message = _("Image(s) added")

return status, message, new_context