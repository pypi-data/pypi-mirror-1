## Controller Python Script "widget_attachmentsmanager_moveup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=attachmentIds=[]
##title=Move attachments up

message = context.doMoveUpAttachments(attachmentIds)

return state.set(status = 'success',
                 portal_status_message = message)
