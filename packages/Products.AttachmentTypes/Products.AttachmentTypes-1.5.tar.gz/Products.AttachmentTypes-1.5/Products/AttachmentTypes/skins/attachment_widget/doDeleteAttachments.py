## Controller Python Script "doDeleteAttachments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Delete attachments

from Products.CMFPlone import PloneMessageFactory as _

status = 'success'
message = ''

# Delete attachments
ids = []
for attachment in attachmentIds:
    if attachment.has_key('id'):
        ids.append(attachment['id'])

if len(ids) > 1:
   message = _('%d attachments deleted') % len(ids)
elif len(ids) == 1:
   message = _('Attachment deleted')
else:
    status = 'failure'
    message = _('You must select at least one attachment to delete.')

context.manage_delObjects(ids)

return status, message