## Controller Python Script "widget_attachmentsmanager_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Upload new attachments
##

request = context.REQUEST

status, message, new_context = context.doAddAttachments(attachmentFiles=request.get('attachmentFiles', None))

# Because we may have brough an object out of the portal_factory, we need
# to fiddle the action manually here

templateName = request['PATH_INFO'].split('/')[-1]
targetPath = '/'.join(new_context.getPhysicalPath()) + '/' + templateName

return state.set(context = new_context,
                  status = 'uploaded',
                  portal_status_message = message,
                  next_action = 'traverse_to:string:%s' % targetPath)
