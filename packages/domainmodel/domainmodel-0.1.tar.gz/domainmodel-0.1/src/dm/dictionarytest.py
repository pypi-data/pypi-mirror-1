import dm.dictionary
from dm.dictionarywords import *
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestSystemDictionary),
    ]
    return unittest.TestSuite(suites)


class TestSystemDictionary(unittest.TestCase):

    def setUp(self):
        self.dictionary = dm.dictionary.SystemDictionary()

    def test_system_name(self):
        self.failUnlessEqual(self.dictionary[SYSTEM_NAME], 'domainmodel')

