import unittest
import desire.testunit
from dm.view.rpctest import AutocompleterViewTestCase
from dm.view.rpctest import AutoappenderViewTestCase
from desire.django.apps.eui.views.rpc import RegistryAutocompleterView
from desire.django.apps.eui.views.rpc import RegistryAutocompleter
from desire.django.apps.eui.views.rpc import RegistryAutoappenderView

def suite():
    suites = [
        unittest.makeSuite(TestRegistryAutocompleterView),
        unittest.makeSuite(TestRegistryAutoappenderView),
    ]
    return unittest.TestSuite(suites)


class TestRegistryAutocompleterView(AutocompleterViewTestCase):

    postQueryName = 'queryString'
    viewClass = RegistryAutocompleterView
    postQueryString = 'RegistryAutocomplete2'
    requiredResponseContent = None
    registryPath = None

    def initPost(self):
        super(TestRegistryAutocompleterView, self).initPost()
        self.POST['registryPath'] = self.registryPath

    def createAutocompleter(self):
        return RegistryAutocompleter()

    def setUp(self):
        collections = self.registry.collections
        products = self.registry.products
        self.collection = collections.create(
            description='TestRegistryAutocomplete')
        self.product1 = products.create(
            description='RegistryAutocomplete1')
        self.product2 = products.create(
            description='RegistryAutocomplete2')
        self.registryPath = 'collections/%s/products' % self.collection.getRegisterKeyValue()
        self.requiredResponseContent = '["RegistryAutocomplete2 (#%s)"]' % self.product2.id
        super(TestRegistryAutocompleterView, self).setUp()

    def tearDown(self):
        super(TestRegistryAutocompleterView, self).tearDown()
        self.product2.delete()
        self.product1.delete()
        self.collection.delete()


class TestRegistryAutoappenderView(AutoappenderViewTestCase):

    viewClass = RegistryAutoappenderView
    
    def checkResponseContent(self):
        self.requiredResponseContent = '"OK"'
        self.failUnlessResponseContent()

# Todo: Test appending registers keyed by domain object.
