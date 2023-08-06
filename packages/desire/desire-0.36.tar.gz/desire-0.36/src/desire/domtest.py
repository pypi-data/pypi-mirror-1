import unittest
import desire.testunit
import desire.dom.buildertest

def suite():
    suites = [
        desire.dom.buildertest.suite(),
    ]
    return unittest.TestSuite(suites)

