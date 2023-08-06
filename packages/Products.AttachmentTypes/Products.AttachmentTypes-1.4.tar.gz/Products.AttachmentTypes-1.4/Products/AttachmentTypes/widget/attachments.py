from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.AttachmentTypes.utils import getAttachments

class AttachmentsManagerWidget(TypesWidget):

    security = ClassSecurityInfo()

    def getAttachments(self, context):
        return getAttachments(context)
    
    security.declarePublic('isVisible')
    def isVisible(self, instance, mode='view'):
        """
        """
        if instance.isTemporary():
            return 'invisible'
        return TypesWidget.isVisible(self, instance, mode)

    # Use the base class properties, and add two of our own
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro'     : 'widget_attachmentsmanager',
                        'expanded'  : False,
                        },)

# Register the widget with Archetypes
registerWidget(AttachmentsManagerWidget,
               title = 'Attachments manager widget',
               description= ('Renders controls for uploading attachments to documents',),
               used_for = ('Products.Archetypes.Field.BooleanField',)
               )
