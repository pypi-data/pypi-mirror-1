from Products.Five import BrowserView
from plone.schemaeditor.interfaces import IEditableSchema
from zope.app.container.contained import notifyContainerModified
from zope.event import notify
from zope.app.container.contained import ObjectRemovedEvent

class FieldOrderView(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.field = context.field
        self.schema = context.field.interface
    
    def move(self, pos):
        """ AJAX method to change field position within its schema.
        """
        
        schema = IEditableSchema(self.schema)
        fieldname = self.field.__name__
        schema.move_field(fieldname, int(pos))
        notifyContainerModified(self.schema)

    def move_up(self):
        """
        method to move field up
        this is used when user does not have js enabled
        """
        pass
        
    def move_down(self):
        """
        method to move field down
        this is used when user does not have js enabled
        """
        pass

    def delete(self):
        """
        AJAX method to delete a field
        """
        schema = IEditableSchema(self.schema)
        schema.remove_field(self.field.getName())
        notify(ObjectRemovedEvent(self.field, self.schema))