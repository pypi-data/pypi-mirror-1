import unittest
import dm.testunit
import dm.django.settingstest

def suite():
    "Return a TestSuite of dm.db TestCases."
    suites = [
        dm.django.settingstest.suite(),
    ]
    return unittest.TestSuite(suites)

