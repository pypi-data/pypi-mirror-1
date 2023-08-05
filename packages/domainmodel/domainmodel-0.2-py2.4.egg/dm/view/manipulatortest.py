import unittest
from dm.view.testunit import TestCase
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.ioc import *
from dm.util.datastructure import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestDomainObjectManipulator),
#        unittest.makeSuite(TestDomainObjectManipulatorCreate),
#        unittest.makeSuite(TestDomainObjectManipulatorUpdate),
#        unittest.makeSuite(TestHasManyManipulator),
    ]
    return unittest.TestSuite(suites)


class ManipulatorTestCase(TestCase):

    def setUp(self):
        super(ManipulatorTestCase, self).setUp()
        self.manipulator = self.buildManipulator()

    def tearDown(self):
        self.manipulator = None
        super(ManipulatorTestCase, self).tearDown()
    
    def test_exists(self):
        self.failUnless(self.manipulator)
        self.failUnless(self.manipulator.fields)
    
    def buildManipulator(self):
        raise "Abstract method not implemented."


class DomainObjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'DomainObjectManipulatorTestCase'

    def setUp(self):
        super(DomainObjectManipulatorTestCase, self).setUp()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['fullname'] = 'DomainObject Manipulator TestCase'
        self.validData['password'] = 'password'
        self.validData['email'] = 'noreply@appropriatesoftware.net'
        self.validData['role'] = 'Visitor'
        self.validData['state'] = 'active'
        self.validData.setlist('memberships', ['administration', 'example'])
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(DomainObjectManipulatorTestCase, self).tearDown()
        if self.fixtureName in self.registry.persons.getAll():
            person = self.registry.persons.getAll()[self.fixtureName]
            person.delete()
            person.purge()

    def buildManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.persons)


class TestDomainObjectManipulator(DomainObjectManipulatorTestCase):

    def testGetValidationErrors(self):
        errors = self.manipulator.getValidationErrors(self.validData)
        self.failIf(errors, str(errors))
        errors = self.manipulator.getValidationErrors(self.invalidData)
        self.failUnless(errors, str(errors))

    def testDecodeHtml(self):
        self.manipulator.decodeHtml(self.validData)


class TestDomainObjectManipulatorCreate(DomainObjectManipulatorTestCase):

    def setUp(self):
        super(TestDomainObjectManipulatorCreate, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
        self.failUnlessEqual(person.fullname, self.validData['fullname'])
        self.failUnlessEqual(person.email, self.validData['email'])
        self.failUnlessEqual(person.role.getRegisterKeyValue(), self.validData['role'])
        adminProject = self.registry.projects['administration']
        self.failUnless(adminProject in person.memberships)


class TestDomainObjectManipulatorUpdate(DomainObjectManipulatorTestCase):

    def setUp(self):
        super(TestDomainObjectManipulatorUpdate, self).setUp()
        self.manipulator.create(self.validData)
        objectRegister = self.registry.persons
        domainObject = self.manipulator.domainObject
        self.manipulator = None
        self.manipulator = DomainObjectManipulator(
            objectRegister=objectRegister,
            domainObject=domainObject,
        )
        
    def testUpdateString(self):
        self.validData['fullname'] = 'Update ' + self.validData['fullname']
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.fullname, self.validData['fullname'])

    def testUpdateHasA(self):
        self.validData['role'] = 'Developer'
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.role.getRegisterKeyValue(), self.validData['role'])

    def testUpdateHasMany(self):
        self.validData.setlist('memberships', ['example'])
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        adminProject = self.registry.projects['administration']
        self.failIf(adminProject in person.memberships)


class HasManyManipulatorTestCase(ManipulatorTestCase):

    projectName = 'warandpeace'
    personName = 'levin'
    roleName = 'Developer'

    def setUp(self):
        super(HasManyManipulatorTestCase, self).setUp()
        self.person = self.registry.persons[self.personName]
        self.validData = MultiValueDict()
        self.validData['person'] = self.personName
        self.validData['role'] = self.roleName
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(HasManyManipulatorTestCase, self).tearDown()
        if self.person in self.project.members:
            membership = self.project.members[self.person]
            membership.delete()
            membership.purge()

    def buildManipulator(self):
        self.project = self.registry.projects[self.projectName]
        return HasManyManipulator(objectRegister=self.project.members)


class TestHasManyManipulator(HasManyManipulatorTestCase):

    def testGetValidationErrors(self):
        errors = self.manipulator.getValidationErrors(self.validData)
        self.failIf(errors, str(errors))
        errors = self.manipulator.getValidationErrors(self.invalidData)
        self.failUnless(errors, str(errors))

    def testDecodeHtml(self):
        self.manipulator.decodeHtml(self.validData)

