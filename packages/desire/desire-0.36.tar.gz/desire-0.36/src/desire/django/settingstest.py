import unittest
import desire.django.settings.main as settings
import desire.django.settings.urls.eui as urls

def suite():
    suites = [
        unittest.makeSuite(TestSettings),
        unittest.makeSuite(TestUrls),
    ]
    return unittest.TestSuite(suites)


class TestSettings(unittest.TestCase):

    def test_main(self):
        # stable actual values, check for correct value
        # todo: Move test to domainmodel package.
        #self.failUnlessEqual(settings.TIME_ZONE, 'Europe/Paris')
        # todo: Move test to domainmodel package.
        #self.failUnlessEqual(settings.SECRET_KEY, 'f*(d3d45zetsb3)$&2h5@%lua()yc+kfn4w^dmrf_j1i(6jjkq')
        # todo: Move test to domainmodel package.
        #self.failUnlessEqual(settings.ROOT_URLCONF, 'desire.django.settings.urls.main')

        # unstable actual values, check for any value
        self.failUnless(settings.TEMPLATE_DIRS)

        # abstract settings, check for null value


class TestUrls(unittest.TestCase):

    def test_main(self):
        self.failUnless(urls)
        self.failUnless(urls.urlpatterns)

