from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.AttachmentTypes.utils import getImages

class ImagesManagerWidget(TypesWidget):

    security = ClassSecurityInfo()

    def getImages(self, context):
        return getImages(context)
    
    security.declarePublic('isVisible')
    def isVisible(self, instance, mode='view'):
        """
        """
        try:
            if instance.isTemporary():
                return 'invisible'
        except:
            pass
        return TypesWidget.isVisible(self, instance, mode)

    # Use the base class properties, and add two of our own
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro'     : 'widget_imagesmanager',
                        'expanded'  : False,
                        },)

# Register the widget with Archetypes
registerWidget(ImagesManagerWidget,
               title = 'Images manager widget',
               description= ('Renders controls for uploading images in documents',),
               used_for = ('Products.Archetypes.Field.BooleanField',)
               )
