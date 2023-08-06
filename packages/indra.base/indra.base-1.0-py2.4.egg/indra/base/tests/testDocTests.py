import unittest
import doctest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
            doctest.DocFileSuite("indrabase.txt",
                package="indra.base.tests",
                )
            )
    return suite
