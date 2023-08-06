from zope import interface
import zope.event
import zope.schema.fieldproperty

import bbb

class IFieldModifiedEvent(bbb.IObjectEvent):
    """Triggered when a field has been modified."""

    new = interface.Attribute('New field value')
    old = interface.Attribute('Old field value')

class FieldModifiedEvent(bbb.ObjectEvent):
    interface.implements(IFieldModifiedEvent)

    def __init__(self, context, new, old):
        super(FieldModifiedEvent, self).__init__(context)
        self.new = new
        self.old = old

class EventProperty(zope.schema.fieldproperty.FieldProperty):

    def __init__(self, field, name=None, event=FieldModifiedEvent):
        super(EventProperty, self).__init__(field, name=None)
        self.event = event

    def __set__(self, instance, value):
        old = self.__get__(instance, type(instance))
        super(EventProperty, self).__set__(instance, value)
        self.notify(instance, value, old)

    def notify(self, instance, new, old):
        if self.event is not None and new != old:
            zope.event.notify(self.event(instance, new, old))
