## Controller Python Script "widget_attachmentsmanager_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Delete attachments

status, message = context.doDeleteAttachments(attachmentIds)

return state.set(status = status,
                 portal_status_message = message)
