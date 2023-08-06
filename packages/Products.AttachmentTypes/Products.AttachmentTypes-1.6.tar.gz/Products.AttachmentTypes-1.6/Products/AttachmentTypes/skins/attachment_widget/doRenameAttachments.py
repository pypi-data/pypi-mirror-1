## Controller Python Script "doRenameAttachments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=attachmentTitles=[]
##title=Rename attachments

from Products.CMFPlone import PloneMessageFactory as _

message = _("No attachment selected")

for attachmentTitle in attachmentTitles:
    message = _("Attachment(s) renamed")
    if attachmentTitle.has_key('title') and attachmentTitle['title'] != '':
        item = getattr(context, attachmentTitle['id'])
        item.setTitle(attachmentTitle['title'])
        item.reindexObject(idxs = ['Title'])

return message