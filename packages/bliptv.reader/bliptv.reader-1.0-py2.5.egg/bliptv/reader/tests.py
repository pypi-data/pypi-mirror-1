import unittest
import doctest

optionflags = doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite(
                "README.txt",
                package="bliptv.reader",
                optionflags=optionflags,
                )
            )

    return suite