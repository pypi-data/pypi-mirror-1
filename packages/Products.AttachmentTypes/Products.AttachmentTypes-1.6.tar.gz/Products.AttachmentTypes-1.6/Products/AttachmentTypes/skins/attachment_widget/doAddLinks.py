## Controller Python Script "doAddLinks"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=links=None
##title=Add new links
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
message = _("You must enter a Title and Url for the link")

if links:
    for link in links:
        if link.title and link.url:

            title = link.title
            url = link.url

            linkId = plone_utils.normalizeString(title)
            linkId = findUniqueId(linkId)

            newLinkId = new_context.invokeFactory(id = linkId, type_name = 'LinkAttachment')
            if newLinkId is not None and newLinkId != '':
                linkId = newLinkId

            object = getattr(new_context, linkId, None)
            object.setTitle(title)
            object.setRemoteUrl(url)
            object.reindexObject()
            status = 'success'
            message = _("Link(s) added")

return status, message, new_context