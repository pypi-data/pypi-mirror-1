## Controller Python Script "doEditLinks"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=links=[]
##title=Edit links

from Products.CMFPlone import PloneMessageFactory as _

message = _("No link selected.")

for link in links:
    if link.has_key('id'):
        message = _("Changes saved.")
        item = getattr(context, link['id'])
        if link.has_key('title') and link['title'] != '':
            item.setTitle(link['title'])
        if link.has_key('url') and link['url'] != '':
            item.setRemoteUrl(link['url'])
        item.reindexObject()

return message