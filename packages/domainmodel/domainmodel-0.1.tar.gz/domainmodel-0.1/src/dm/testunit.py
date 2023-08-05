"""
Module of extensions to the unittest suite.

(This module wanted to be called dm.unittest but that breaks "import unittest".)

"""

import unittest
import dm.builder
from dm.ioc import *

features.allowReplace = True

class ApplicationTestSuite(unittest.TestSuite):

    appBuilderClass = dm.builder.ApplicationBuilder

    def buildApplication(self):
        appBuilder = self.appBuilderClass()
        appBuilder.construct()
        domBuilder = RequiredFeature('ModelBuilder')
        domBuilder.construct()

    buildApplication = classmethod(buildApplication)
 

class TestCase(unittest.TestCase):

    dictionary   = RequiredFeature('SystemDictionary')
    registry     = RequiredFeature('DomainRegistry')

    def __init__(self, *args, **kwds):
        super(TestCase, self).__init__(*args, **kwds)

