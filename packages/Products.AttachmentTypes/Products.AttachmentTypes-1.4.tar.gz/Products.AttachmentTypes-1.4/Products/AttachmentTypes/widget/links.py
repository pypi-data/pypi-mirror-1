from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.AttachmentTypes.utils import getLinks

class LinksManagerWidget(TypesWidget):

    security = ClassSecurityInfo()

    def getLinks(self, context):
        return getLinks(context)
    
    security.declarePublic('isVisible')
    def isVisible(self, instance, mode='view'):
        """
        """
        if instance.isTemporary():
            return 'invisible'
        return TypesWidget.isVisible(self, instance, mode)

    # Use the base class properties, and add two of our own
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro'     : 'widget_linksmanager',
                        'expanded'  : False,
                        },)

# Register the widget with Archetypes
registerWidget(LinksManagerWidget,
               title = 'Links manager widget',
               description= ('Renders controls for adding links to documents',),
               used_for = ('Products.Archetypes.Field.BooleanField',)
               )
