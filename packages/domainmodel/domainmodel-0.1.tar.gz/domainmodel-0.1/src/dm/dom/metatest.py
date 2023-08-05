import unittest
from dm.dom.testunit import TestCase
import dm.dom.meta

def suite():
    suites = [
        unittest.makeSuite(TestText),
        unittest.makeSuite(TestUrl),
    ]
    return unittest.TestSuite(suites)


class TestText(TestCase):
    
    def setUp(self):
        super(TestText, self).setUp()
        self.field = dm.dom.meta.Text() 
    
    def test_create(self):
        self.failUnless(self.field)
        self.failUnlessEqual(self.field.typeName, 'Text')

class TestUrl(TestCase):
    
    def setUp(self):
        super(TestUrl, self).setUp()
        self.field = dm.dom.meta.Url() 
    
    def test_create(self):
        self.failUnless(self.field)
        self.failUnlessEqual(self.field.typeName, 'Url')

