import unittest

import dm.command.initialise

def suite():
    suites = [
            unittest.makeSuite(InitialiseTest)
        ]
    return unittest.TestSuite(suites)

class InitialiseTest(unittest.TestCase):
    
    def setUp(self):
        self.cmd = dm.command.initialise.InitialiseDomainModel()
    
    def test_setUpTestFixtures(self):
        self.failUnless(self.cmd)
        
