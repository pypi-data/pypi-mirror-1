## Controller Python Script "doMoveDownAttachments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Move attachments down

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

plone_utils = getToolByName(context, 'plone_utils')

ids = []
for attachment in attachmentIds:
    if attachment.has_key('id'):
        ids.append(attachment)

message = _("No attachment selected")

if len(ids) > 0:
    message = _("Attachment(s) moved down.")
    pos = int(ids[-1]['downPos'])
    for attachment in ids:
        context.moveObjectToPosition(attachment['id'], pos)

plone_utils.reindexOnReorder(context)

return message