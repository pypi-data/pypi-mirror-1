import unittest
import desire.testunit
import desire.django.apps.eui.views.registrytest
import desire.django.apps.eui.views.rpctest

def suite():
    suites = [
        desire.django.apps.eui.views.registrytest.suite(),
        desire.django.apps.eui.views.rpctest.suite(),
    ]
    return unittest.TestSuite(suites)

