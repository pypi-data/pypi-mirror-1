import dm.dictionary
from dm.dictionarywords import *
import unittest
import os

def suite():
    suites = [
        unittest.makeSuite(TestSystemDictionary),
    ]
    return unittest.TestSuite(suites)


class TestSystemDictionary(unittest.TestCase):

    def setUp(self):
        self.dictionary = dm.dictionary.SystemDictionary()

    def test_systemName(self):
        self.failUnlessEqual(self.dictionary[SYSTEM_NAME], 'domainmodel')
        imagesPath = self.dictionary[IMAGES_DIR_PATH]
        self.failUnless(os.path.exists(imagesPath), imagesPath)

