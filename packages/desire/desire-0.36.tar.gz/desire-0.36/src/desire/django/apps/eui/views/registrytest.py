import unittest
import desire.testunit
from dm.view.basetest import AdminSessionViewTestCase
from desire.django.apps.eui.views.registry import *

def suite():
    suites = [
        unittest.makeSuite(TestCollectionListView),
    ]
    return unittest.TestSuite(suites)


# Todo: Extract to domainmodel.
class RegistryViewTestCase(AdminSessionViewTestCase):

    def createViewKwds(self):
        viewKwds = super(RegistryViewTestCase, self).createViewKwds()
        viewKwds['registryPath'] = self.registryPath
        return viewKwds

class TestCollectionListView(RegistryViewTestCase):

    viewClass = DesireRegistryListView
    registryPath = 'collections'


