"""A field for a file like object."""

from zope import interface, schema
import zope.schema.interfaces

class IFile(zope.schema.interfaces.IBytes):
    """A file like object."""

class File(schema.Bytes):
    interface.implements(IFile)

    # Cannot validate type this way
    _type = object

    def __init__(self, min_length=None, **kw):
        # Generally don't want to check the length
        # Note that if you do, the widget will need to return an object
        # that responds to len()
        super(File, self).__init__(min_length=min_length, **kw)

    def _validate(self, value):
        super(File, self)._validate(value)
        if not (hasattr(value, 'read') and hasattr(value, 'seek')):
            raise zope.schema.interfaces.WrongType(
                value, 'Not a file like object')

