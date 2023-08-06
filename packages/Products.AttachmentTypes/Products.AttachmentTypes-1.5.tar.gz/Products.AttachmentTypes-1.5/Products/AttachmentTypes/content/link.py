from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.public import registerType

class LinkAttachment(ATLink):
    """A link attachment"""
    portal_type = meta_type = 'LinkAttachment'

registerType(LinkAttachment)

