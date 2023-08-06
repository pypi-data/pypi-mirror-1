## Controller Python Script "widget_linksmanager_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=links=[]
##title=Edit links

message = context.doEditLinks(links)

return state.set(status = 'success',
                 portal_status_message = message)
