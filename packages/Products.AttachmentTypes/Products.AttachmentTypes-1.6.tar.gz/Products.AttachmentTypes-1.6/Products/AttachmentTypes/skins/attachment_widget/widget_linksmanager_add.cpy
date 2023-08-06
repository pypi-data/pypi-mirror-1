## Controller Python Script "widget_linksmanager_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Add new links
##

request = context.REQUEST

status, message, new_context = context.doAddLinks(links=request.get('links', None))

# Because we may have brough an object out of the portal_factory, we need
# to fiddle the action manually here

templateName = request['PATH_INFO'].split('/')[-1]
targetPath = '/'.join(new_context.getPhysicalPath()) + '/' + templateName

return state.set(context = new_context,
                  status = 'added',
                  portal_status_message = message,
                  next_action = 'traverse_to:string:%s' % targetPath)
