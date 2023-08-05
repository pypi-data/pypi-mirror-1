import dm.environment
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestSystemEnvironment),
    ]
    return unittest.TestSuite(suites)


class TestSystemEnvironment(unittest.TestCase):

    systemName = 'domainmodel'

    def setUp(self):
        self.environment = dm.environment.SystemEnvironment(self.systemName)

    def test_assertDjangoSettingsModule(self):
        self.environment.assertDjangoSettingsModule()

    def test_getConfigFilePathEnvironmentVariableName(self):
        exp = 'DOMAINMODEL_SETTINGS'
        out = self.environment.getConfigFilePathEnvironmentVariableName()
        self.failUnlessEqual(exp, out)

