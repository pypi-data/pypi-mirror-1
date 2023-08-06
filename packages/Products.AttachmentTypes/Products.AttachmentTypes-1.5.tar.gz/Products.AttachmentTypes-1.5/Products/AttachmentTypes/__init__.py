from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import DirectoryView
from Products.AttachmentTypes.config import *

DirectoryView.registerDirectory('skins', globals())

def initialize(context):

    # Import the type, which results in registerType() being called
    from content import ImageAttachment, FileAttachment, LinkAttachment

    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)