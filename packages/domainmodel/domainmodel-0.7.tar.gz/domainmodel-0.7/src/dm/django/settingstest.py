import unittest
import dm.django.settings.main as settings

def suite():
    suites = [
        unittest.makeSuite(TestSettings),
        unittest.makeSuite(TestUrls),
    ]
    return unittest.TestSuite(suites)

class TestSettings(unittest.TestCase):

    def test_main(self):
        # stable actual values, check for correct value
        self.failUnlessEqual(settings.TIME_ZONE, 'Europe/Paris')
        
        # unstable actual values, check for any value
        self.failUnless(settings.SECRET_KEY)
        self.failUnless(settings.TEMPLATE_DIRS)

        # abstract settings, check for null value
        self.failUnlessEqual(settings.ROOT_URLCONF, '')

class TestUrls(unittest.TestCase):
    
    pass


