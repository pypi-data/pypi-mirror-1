import unittest
import desire.domtest
import desire.djangotest
import desire.tracclienttest

def suite():
    suites = [
        desire.domtest.suite(),
        desire.djangotest.suite(),
        desire.tracclienttest.suite()
    ]
    return unittest.TestSuite(suites)

