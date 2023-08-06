import unittest
from zope.testing import doctest 
import zope.component.testing

def test_suite():
    suite = doctest.DocFileSuite(
        'interface.txt',
        'event.txt',
        setUp=zope.component.testing.setUp,
        tearDown=zope.component.testing.tearDown,
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
