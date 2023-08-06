import unittest
import desire.testunit
import desire.django.settingstest
import desire.django.apps.eui.viewstest

def suite():
    suites = [
        desire.django.settingstest.suite(),
        desire.django.apps.eui.viewstest.suite(),
    ]
    return unittest.TestSuite(suites)

