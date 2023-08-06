from zope import interface

try:
    from zope.component import interface as component_iface
except ImportError:
    from zope.app.component import interface as component_iface

try:
    from zope.component.interfaces import IObjectEvent, ObjectEvent
except ImportError:
    from zope.app.event.interfaces import IObjectEvent
    from zope.app.event.objectevent import ObjectEvent

try:
    from zope.interface import noLongerProvides
except:
    def noLongerProvides(object, iface):
        interface.directlyProvides(
            object, interface.directlyProvidedBy(object)-iface)
