"""
Module of extensions to the unittest suite.

(This module wanted to be called dm.unittest but that breaks "import unittest".)

"""

import unittest
import dm.builder
from dm.ioc import *

features.allowReplace = True

class SystemModeError(Exception):
    pass

class ApplicationTestSuite(unittest.TestSuite):

    appBuilderClass = dm.builder.ApplicationBuilder

    def buildApplication(self):
        appBuilder = self.appBuilderClass()
        appBuilder.construct()
        registry = RequiredFeature('DomainRegistry')
        if registry != None:
            domBuilder = RequiredFeature('ModelBuilder')
            domBuilder.construct()
        dictionary = RequiredFeature('SystemDictionary')
        if dictionary != None:
            currentSystem = registry.systems.getSortedList()[-1]
            requiredSystemModeName = 'development'
            if currentSystem.mode != requiredSystemModeName:
                configFilePath = dictionary.environment.getConfigFilePath()
                raise SystemModeError("The system was built in '%s' mode. The system must be built in '%s' mode for the test suite to be run. Please check the 'system_mode' setting in your configuration file '%s' and rebuild the database." % (currentSystem.mode, requiredSystemModeName, configFilePath))

    buildApplication = classmethod(buildApplication)
 

class TestCase(unittest.TestCase):

    dictionary   = RequiredFeature('SystemDictionary')
    registry     = RequiredFeature('DomainRegistry')

    def __init__(self, *args, **kwds):
        super(TestCase, self).__init__(*args, **kwds)

