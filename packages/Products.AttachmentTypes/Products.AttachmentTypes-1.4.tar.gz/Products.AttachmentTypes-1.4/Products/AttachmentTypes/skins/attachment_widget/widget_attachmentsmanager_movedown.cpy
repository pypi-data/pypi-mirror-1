## Controller Python Script "widget_attachmentsmanager_movedown"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Move attachments down

message = context.doMoveDownAttachments(attachmentIds)

return state.set(status = 'success',
                 portal_status_message = message)
