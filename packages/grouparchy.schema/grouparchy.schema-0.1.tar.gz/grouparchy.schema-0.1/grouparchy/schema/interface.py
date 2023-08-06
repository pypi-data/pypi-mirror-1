from zope import interface, component, schema, event
import zope.interface.interfaces
import zope.schema.interfaces
from zope.schema import vocabulary, fieldproperty
import zope.dottedname.resolve
import zope.publisher.interfaces.browser
import zope.app.form.browser.interfaces

import grouparchy.schema.event
import bbb

_default = object()

class IInterfacesContext(interface.Interface):
    """The context providing the interfaces."""

class IInterfacesSource(zope.schema.interfaces.IIterableSource):
    """A source for interfaces, optionally of a certain type."""

class InterfaceTerms(object):
    """Map identifiers to interfaces and vice versa."""
    interface.implements(zope.app.form.browser.interfaces.ITerms)
    component.adapts(
        IInterfacesSource,
        zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        pass

    def getTerm(self, value):
        """Return the identifier for the given interface."""
        return vocabulary.SimpleTerm(
            value, value.__identifier__, title=value.__name__)

    def getValue(self, token):
        """Return the interface for the given identifier."""
        return zope.dottedname.resolve.resolve(token)

class InterfacesSource(object):
    interface.implements(IInterfacesSource)

    def __init__(self,
                 iface_type=zope.interface.interfaces.IInterface):
        self.iface_type = iface_type

    def __iter__(self):
        for id, iface in component.getUtilitiesFor(self.iface_type):
            yield iface

class IInterfacesModified(
    grouparchy.schema.event.IFieldModifiedEvent):
    """Provided interfaces have been modified"""

    added = schema.Tuple(title=u'Interfaces Newly Provided')
    removed = schema.Tuple(title=u'Interfaces No Longer Provided')

_omitted = interface.Declaration()
class InterfacesModified(grouparchy.schema.event.FieldModifiedEvent):
    interface.implements(IInterfacesModified)

    def __init__(self, context, new=_omitted, old=_omitted,
                 added=_omitted, removed=_omitted):
        super(InterfacesModified, self).__init__(context, new, old)
        self.added = added
        self.removed = removed

class IInterfacesAdded(IInterfacesModified):
    """Provided interfaces have been added where there were some
    before but none removed"""

class InterfacesAdded(InterfacesModified):
    interface.implements(IInterfacesAdded)

class IInterfacesPopulated(IInterfacesAdded):
    """Interfaces have been provided where none were previously"""

class InterfacesPopulated(InterfacesModified):
    interface.implements(IInterfacesPopulated)

class IInterfacesRemoved(IInterfacesModified):
    """Provided interfaces have been removed where there are still some
    provided but none added"""

class InterfacesRemoved(InterfacesModified):
    interface.implements(IInterfacesRemoved)

class IInterfacesCleared(IInterfacesRemoved):
    """All provided interfaces have been removed"""

class InterfacesCleared(InterfacesModified):
    interface.implements(IInterfacesCleared)

class IInterfacesChanged(IInterfacesAdded, IInterfacesRemoved):
    """Some provided interfaces have been added and removed where there
    are still some provided and where there were some before"""

class InterfacesChanged(InterfacesModified):
    interface.implements(IInterfacesChanged)

class InterfacesField(schema.Set):
    """A field for managing all interfaces of a certain type."""
    _type = set, tuple, list

    def __init__(self, value_type=None, **kw):
        if not isinstance(value_type, (schema.InterfaceField,
                                       schema.Choice)):
            raise ValueError(
                "'value_type' must be an InterfaceField or a Choice.")
        super(InterfacesField, self).__init__(
            value_type=value_type, **kw)

@interface.implementer(IInterfacesContext)
@component.adapter(interface.Interface)
def getInterfacesContext(obj):
    """Check some common names for the context on adapters."""
    for name in ('context', 'object'):
        if hasattr(obj, name):
            return getattr(obj, name)
    return obj

class InterfacesProperty(grouparchy.schema.event.EventProperty):

    populated = InterfacesPopulated
    cleared = InterfacesCleared
    added = InterfacesAdded
    removed = InterfacesRemoved
    changed = InterfacesChanged

    def __init__(self, field, name=None, event=_default):
        super(InterfacesProperty, self).__init__(field, name=name,
                                                 event=event)

    def __get__(self, inst, klass):
        if inst is None:
            return self
        field = self._FieldProperty__field.bind(inst)
        vocab = getattr(getattr(field, 'value_type',
                                fieldproperty._marker),
                        'vocabulary', fieldproperty._marker)
        context = IInterfacesContext(inst, inst)
        if vocab is fieldproperty._marker:
            return interface.directlyProvidedBy(context)
        else:
            return interface.Declaration(iface for iface in
                         interface.directlyProvidedBy(context)
                         if iface in vocab)

    def __set__(self, inst, value):
        field = self._FieldProperty__field.bind(inst)
        field.validate(value)
        if (field.readonly
            and self._FieldProperty__name in inst.__dict__):
            raise ValueError(self._FieldProperty__name,
                             'field is readonly')

        old = InterfacesProperty.__get__(self, inst, type(inst))
        new = interface.Declaration(*value)
        previous = set(old)
        current = set(value)

        removed = previous.difference(current)
        removed = interface.Declaration(
            *(iface for iface in old if iface in removed))

        added = current.difference(previous)
        added = interface.Declaration(
            *(iface for iface in value if iface in added))

        context = IInterfacesContext(inst, inst)

        for iface in removed:
            bbb.noLongerProvides(context, iface)

        interface.alsoProvides(context, *added)

        self.notify(context, new, old, added, removed)

    def notify(self, context, new, old, added, removed):
        if self.event is not _default:
            # Event passed in, defer to EventProperty style
            return super(InterfacesProperty, self).notify(context,
                                                          new, old)
        elif not (added or removed):
            # don't trigger events if nothing is changed
            return

        if tuple(old) == ():
            class_ = self.populated
        elif tuple(new) == ():
            class_ = self.cleared
        elif tuple(removed) == ():
            class_ = self.added
        elif tuple(added) == ():
            class_ = self.removed
        else:
            class_ = self.changed
        event.notify(class_(context, new, old, added, removed))

class InterfaceIdentsProperty(InterfacesProperty):

    def __get__(self, inst, klass):
        return tuple(
            iface.__identifier__
            for iface in super(InterfaceIdentsProperty,
                               self).__get__(inst, klass))

    def __set__(self, inst, value):
        super(InterfaceIdentsProperty, self).__set__(
            inst, tuple(zope.dottedname.resolve.resolve(dotted)
                        for dotted in value))

InterfaceUtilitiesSource = InterfacesSource()

class IDirectlyProvided(interface.Interface):
    """Manage the interfaces directly provided by the context"""

    directlyProvided = InterfacesField(
        title=u'Directly Provided Interfaces',
        value_type=schema.Choice(source=InterfaceUtilitiesSource))
 
class DirectlyProvided(object):
    interface.implements(IDirectlyProvided)
    component.adapts(interface.Interface)

    directlyProvided = InterfacesProperty(
        IDirectlyProvided['directlyProvided'])

    def __init__(self, context):
        self.context = context

