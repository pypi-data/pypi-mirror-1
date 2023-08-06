import unittest
import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocFileSuite(
            "README.txt",
            optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
            )
        )
    return suite
