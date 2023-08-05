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
        self.failUnlessEqual(
            settings.SECRET_KEY,
            '(*YZF@{ZFHW$Rli(EFH(*SEHF(&9S(P&SYGDF(&G9Ged9f7gs'
        )
        
        # unstable actual values, check for any value
        self.failUnless(settings.TEMPLATE_DIRS, "Template dirs not set.")

        # abstract settings, check for null value
        self.failUnlessEqual(settings.ROOT_URLCONF, '')

class TestUrls(unittest.TestCase):
    
    pass


