import unittest
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('p4a.plonetagging.l10nutils',
                             optionflags=doctest.ELLIPSIS),
        doctest.DocTestSuite('p4a.plonetagging.utils',
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
