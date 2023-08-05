import unittest
from dm.testunit import TestCase
from dm.strategy import MakeProtectedName
from dm.strategy import MakeProtectedNames
from dm.strategy import FindProtectionObject
from dm.strategy import FindProtectionObjects
from dm.strategy import FindInstanceProtectionObject
from dm.strategy import CreateProtectionObject
from dm.strategy import MakeCheckString
from dm.strategy import MakeCookieString
from dm.strategy import ValidateCookieString

def suite():
    suites = [
        unittest.makeSuite(TestMakeProtectedName),
        unittest.makeSuite(TestMakeProtectedNames),
        unittest.makeSuite(TestFindProtectionObject),
        unittest.makeSuite(TestFindProtectionObjects),
        unittest.makeSuite(TestFindInstanceProtectionObject),
        unittest.makeSuite(TestCreateProtectionObject),
        unittest.makeSuite(TestMakeCheckString),
        unittest.makeSuite(TestMakeCookieString),
    ]
    return unittest.TestSuite(suites)


class TestMakeProtectedName(TestCase):

    def testProtectedDomainObject(self):
        self.protectedObject = self.registry.systems[1]
        makeName = MakeProtectedName(self.protectedObject)
        protectedName = makeName.make()
        self.failUnlessEqual(protectedName, 'System.1')
    
        self.protectedObject = self.registry.plugins['accesscontrol']
        self.failUnlessEqual(self.protectedObject.id, 1)
        self.failUnlessEqual(self.protectedObject.name, 'accesscontrol')
        makeName = MakeProtectedName(self.protectedObject)
        protectedName = makeName.make()
        self.failUnlessEqual(protectedName, 'Plugin.1')
        
    def testProtectedDomainObjectClass(self):
        self.protectedObject = self.registry.getDomainClass('System')
        makeName = MakeProtectedName(self.protectedObject)
        protectedName = makeName.make()
        self.failUnlessEqual(protectedName, 'System')


class TestMakeProtectedNames(TestCase):

    def testProtectedDomainObject(self):
        self.protectedObject = self.registry.systems[1]
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        self.failUnlessEqual(protectedNames[0], 'System.1')
        self.failUnlessEqual(protectedNames[1], 'System')
    
        self.protectedObject = self.registry.plugins['accesscontrol']
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        self.failUnlessEqual(protectedNames[0], 'Plugin.1')
        self.failUnlessEqual(protectedNames[1], 'Plugin')
        
    def testProtectedDomainObjectClass(self):
        self.protectedObject = self.registry.getDomainClass('System')
        makeNames = MakeProtectedNames(self.protectedObject)
        protectedNames = makeNames.make()
        self.failUnlessEqual(protectedNames[0], 'System')


class TestFindProtectionObject(TestCase):

    def testProtectedDomainObject(self):
        protectedObject = self.registry.systems[1]
        findObject = FindProtectionObject(protectedObject)
        protectionObject = findObject.find()
        self.failUnlessEqual(protectionObject.name, 'System')
    
        protectedObject = self.registry.plugins['accesscontrol']
        findObject = FindProtectionObject(protectedObject)
        protectionObject = findObject.find()
        self.failUnlessEqual(protectionObject.name, 'Plugin')
    
    def testProtectedDomainObjectClass(self):
        protectedObject = self.registry.getDomainClass('System')
        findObject = FindProtectionObject(protectedObject)
        protectionObject = findObject.find()
        self.failUnlessEqual(protectionObject.name, 'System')
        

class TestFindProtectionObjects(TestCase):

    def testProtectedDomainObject(self):
        protectedObject = self.registry.systems[1]
        findObjects = FindProtectionObjects(protectedObject)
        protectionObjects = findObjects.find()
        self.failUnlessEqual(len(protectionObjects), 1)
        self.failUnlessEqual(protectionObjects[0].name, 'System')
    
        protectedObject = self.registry.plugins['accesscontrol']
        findObjects = FindProtectionObjects(protectedObject)
        protectionObjects = findObjects.find()
        self.failUnlessEqual(len(protectionObjects), 1)
        self.failUnlessEqual(protectionObjects[0].name, 'Plugin')
    
    def testProtectedDomainObjectClass(self):
        protectedObject = self.registry.getDomainClass('System')
        findObjects = FindProtectionObjects(protectedObject)
        protectionObjects = findObjects.find()
        self.failUnlessEqual(len(protectionObjects), 1)
        self.failUnlessEqual(protectionObjects[0].name, 'System')
        
        protectedObject = self.registry.getDomainClass('Plugin')
        findObjects = FindProtectionObjects(protectedObject)
        protectionObjects = findObjects.find()
        self.failUnlessEqual(len(protectionObjects), 1)
        self.failUnlessEqual(protectionObjects[0].name, 'Plugin')
        

class TestFindInstanceProtectionObject(TestCase):

    def testProtectedDomainObject(self):
        protectedObject = self.registry.systems[1]
        findObject = FindInstanceProtectionObject(protectedObject)
        protectionObject = findObject.find()
        self.failIf(protectionObject)
    
    def testProtectedDomainObjectClass(self):
        protectedObject = self.registry.getDomainClass('System')
        findObject = FindInstanceProtectionObject(protectedObject)
        protectionObject = findObject.find()
        self.failIf(protectionObject)
        

class TestCreateProtectionObject(TestCase):

    def testProtectedDomainObject(self):
        pass
    
    def testProtectedDomainObjectClass(self):
        pass
        

class TestMakeCheckString(TestCase):

    plainString = 'TestBlahStringTestBlahStringTest'
    checkString = 'a5177a6957daee6b7a0da6041bbebc43'

    def setUp(self):
        self.checkStringStrategy = MakeCheckString(self.plainString)
        
    def test_make(self):
        checkString = self.checkStringStrategy.make()
        self.failUnlessEqual(checkString, self.checkString)


class TestMakeCookieString(TestCase):

    plainString = 'TestBlahStringTestBlahStringTest'
    cookieString = 'TestBlahStringTestBlahStringTesta5177a6957daee6b7a0da6041bbebc43'

    def setUp(self):
        self.cookieStringStrategy = MakeCookieString(self.plainString)
        
    def test_make(self):
        cookieString = self.cookieStringStrategy.make()
        self.failUnlessEqual(cookieString, self.cookieString)


class TestValidateCookieString(TestCase):

    cookieString = 'TestBlahStringTestBlahStringTesta5177a6957daee6b7a0da6041bbebc43'
    plainString = 'TestBlahStringTestBlahStringTest'

    def setUp(self):
        self.cookieStringStrategy = ValidateCookieString(self.cookieString)
        
    def test_validate(self):
        self.failUnlessEqual(self.cookieStringStrategy.validate(), self.plainString)

