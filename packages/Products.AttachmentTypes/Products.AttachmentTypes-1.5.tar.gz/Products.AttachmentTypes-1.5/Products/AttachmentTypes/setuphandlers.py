from Products.CMFCore.utils import getToolByName

def setupAttachments(context):
    if context.readDataFile('attachmenttypes_various.txt') is None:
        return

    portal = context.getSite()

    # install AttachmentField Product
    inst = getToolByName(portal, 'portal_quickinstaller');
    if not inst.isProductInstalled('AttachmentField'):
        inst.installProduct('AttachmentField')

    # Add FileAttachment and ImageAttachment to kupu's linkable and media types
    kupuTool = getToolByName(portal, 'kupu_library_tool')
    linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
    if 'FileAttachment' not in linkable:
        linkable.append('FileAttachment')
    if 'ImageAttachment' not in linkable:
        linkable.append('ImageAttachment')
    if 'LinkAttachment' not in linkable:
        linkable.append('LinkAttachment')
    # kupu_library_tool has an idiotic interface, basically written purely to
    # work with its configuration page. :-(
    try:
        kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                       'old_type'      : 'linkable',
                                       'portal_types'  :  linkable},))
    except:
        pass

def registerImagesFormControllerActions(context, contentType=None, template='base_edit'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    pfc = getToolByName(context, 'portal_form_controller')
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'AddImages',
                      'traverse_to',
                      'string:widget_imagesmanager_add')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'RenameImages',
                      'traverse_to',
                      'string:widget_attachmentsmanager_rename')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveUp',
                      'traverse_to',
                      'string:widget_attachmentsmanager_moveup')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveDown',
                      'traverse_to',
                      'string:widget_attachmentsmanager_movedown')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteImages',
                      'traverse_to',
                      'string:widget_attachmentsmanager_delete')

def registerAttachmentsFormControllerActions(context, contentType=None, template='base_edit'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    pfc = getToolByName(context, 'portal_form_controller')
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'AddAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_add')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'RenameAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_rename')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveUp',
                      'traverse_to',
                      'string:widget_attachmentsmanager_moveup')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveDown',
                      'traverse_to',
                      'string:widget_attachmentsmanager_movedown')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteAttachments',
                      'traverse_to',
                      'string:widget_attachmentsmanager_delete')


def registerLinksFormControllerActions(context, contentType=None, template='base_edit'):
    """Register the form controller actions necessary for the widget to work.
    This should probably be called from the Install.py script. The parameter
    'context' should be the portal root or another place from which the form
    controller can be acquired. The contentType and template argument allow
    you to restrict the registration to only one content type and choose a
    template other than base_edit, if necessary.
    """
    pfc = getToolByName(context, 'portal_form_controller')
    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'AddLinks',
                      'traverse_to',
                      'string:widget_linksmanager_add')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'EditLinks',
                      'traverse_to',
                      'string:widget_linksmanager_edit')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveUp',
                      'traverse_to',
                      'string:widget_attachmentsmanager_moveup')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'MoveDown',
                      'traverse_to',
                      'string:widget_attachmentsmanager_movedown')

    pfc.addFormAction(template,
                      'success',
                      contentType,
                      'DeleteLinks',
                      'traverse_to',
                      'string:widget_attachmentsmanager_delete')
