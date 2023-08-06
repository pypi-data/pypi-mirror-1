## Controller Python Script "widget_attachmentsmanager_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentTitles=[]
##title=Rename attachments

message = context.doRenameAttachments(attachmentTitles)

return state.set(status = 'success',
                 portal_status_message = message)
