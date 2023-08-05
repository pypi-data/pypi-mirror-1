import unittest
from dm.command.testunit import TestCase
from dm.command.accesscontrol import *
from dm.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestGrantAccess),
        unittest.makeSuite(TestRevokeAccess),
        unittest.makeSuite(TestGrantStandardSystemAccess),
    ]
    return unittest.TestSuite(suites)

class TestAccessControlCommand(TestCase):

    def setUp(self):
        super(TestAccessControlCommand, self).setUp()
        self.roleName = ''
        self.role = None
        self.actionName = ''
        self.action = None
        self.protectedObject = None

    def setRole(self, name):
        self.roleName = name
        self.role = self.registry.roles[name]

    def setAction(self, name):
        self.actionName = name
        self.action = self.registry.actions[name]

    def setProtectedObject(self, className, instanceName=''):
        domainClass = self.registry.getDomainClass(className)
        if instanceName:
            raise "Test method not implemented for instanceName argument."
        else:
            self.protectedObject = domainClass

    def findGrant(self):
        for grant in self.role.grants:
            permission = grant.permission
            if permission.action == self.action:
                protectionObject = permission.protectionObject
                if protectionObject.isProtector(self.protectedObject):
                    return grant
        return None

    def findBar(self):
        for bar in self.role.bars:
            permission = bar.permission
            if permission.action == self.action:
                protectionObject = permission.protectionObject
                if protectionObject.isProtector(self.protectedObject):
                    return bar
        return None


class TestGrantAccess(TestAccessControlCommand):

    def setUp(self):
        super(TestGrantAccess, self).setUp()
        self.setRole('Visitor')
        self.setAction('Purge')
        self.setProtectedObject('Person')

    def tearDown(self):
        grant = self.findGrant()
        if grant:
            grant.delete()
    
    def test_execute(self):
        self.failIf(self.findGrant())
        cmd = GrantAccess(
            self.role, self.actionName, self.protectedObject
        )
        cmd.execute()
        self.failUnless(self.findGrant())


class TestRevokeAccess(TestAccessControlCommand):

    def setUp(self):
        super(TestRevokeAccess, self).setUp()
        self.setRole('Visitor')
        self.setAction('Purge')
        self.setProtectedObject('Person')
        for protectionObject in self.registry.protectionObjects:
            if protectionObject.isProtector(self.protectedObject):
                permission = protectionObject.permissions[self.action]
                self.role.grants.create(permission)

    def tearDown(self):
        grant = self.findGrant()
        if grant:
            grant.delete()
    
    def test_execute(self):
        self.failUnless(self.findGrant())
        cmd = RevokeAccess(
            self.role, self.actionName, self.protectedObject
        )
        cmd.execute()
        self.failIf(self.findGrant())


class TestGrantStandardSystemAccess(TestCase):

    def setUp(self):
        super(TestGrantStandardSystemAccess, self).setUp()
        protectedName = 'ARandomProtectionObject'
        try:
            self.pobj = self.registry.protectionObjects.create(protectedName)
        except:
            pobj = self.registry.protectionObjects[protectedName]
            pobj.delete()
            raise
        cmd = GrantStandardSystemAccess(self.pobj)
        cmd.execute()

    def tearDown(self):
        self.pobj.delete()

    def testPermissionsExist(self):
        for action in self.registry.actions:
            self.failUnless(action in self.pobj.permissions)

    def testGrantExist(self):
        action = self.registry.actions['Read']
        permission = self.pobj.permissions[action]
        role = self.registry.roles['Friend']
        self.failUnless(permission in role.grants)

