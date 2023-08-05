from dm.command.base import Command
from dm.command.state import *
from dm.command.accesscontrol import GrantStandardSystemAccess
from dm.command.person import *

class InitialiseDomainModelBase(Command):

    def execute(self):
        super(InitialiseDomainModelBase, self).execute()
        self.createStates()
        self.createSystem()
        self.createActions()

    def createStates(self):
        self.registry.states.create('pending')
        self.registry.states.create('active')
        self.registry.states.create('deleted')
        
    def createSystem(self):
        self.registry.systems.create(
            version=self.dictionary['system_version'],
            mode=self.dictionary['system_mode'],
        )

    def createActions(self):
        self.registry.actions.create('Create')
        self.registry.actions.create('Read')
        self.registry.actions.create('Update')
        self.registry.actions.create('Delete')
        self.registry.actions.create('Purge')
        

class InitialiseDomainModel(InitialiseDomainModelBase):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
    
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createRoles()
        self.createProtectionObjects()
        self.createGrants()
        self.createRefusals()
        self.createPersons()
        self.createAccessControlPlugin()
        if self.dictionary['system_mode'] == 'development':
            self.createTestPlugins()
            self.setUpTestFixtures()
        self.commitSuccess()

    def createRoles(self):
        roles = self.registry.roles
        self.adminRole     = roles.create('Administrator')
        self.developerRole = roles.create('Developer')
        self.friendRole    = roles.create('Friend')
        self.visitorRole   = roles.create('Visitor')
        
    def createActions(self):
        self.registry.actions.create('Create')
        self.registry.actions.create('Read')
        self.registry.actions.create('Update')
        self.registry.actions.create('Delete')
        self.registry.actions.create('Purge')
        
    def createProtectionObjects(self):
        self.registry.protectionObjects.create('Session')
        self.registry.protectionObjects.create('System')
        self.registry.protectionObjects.create('Person')
        self.registry.protectionObjects.create('Plugin')

    def createGrants(self):
        self.grantAdministratorAccess()
        self.grantRegistrationAccess()
        self.grantStandardSystemAccess('System')
        self.grantStandardSystemAccess('Person')

    def grantAdministratorAccess(self):
        for protectionObject in self.registry.protectionObjects:
            for permission in protectionObject.permissions:
                if not permission in self.adminRole.grants:
                    self.adminRole.grants.create(permission)

    def grantRegistrationAccess(self):
        create = self.registry.actions['Create']
        protectionObjects = self.registry.protectionObjects
        for role in self.registry.roles:
            personProtection = protectionObjects['Person']
            createPerson = personProtection.permissions[create]
            if not createPerson in role.grants:
                role.grants.create(createPerson)

    def grantStandardSystemAccess(self, protectedName):
        protectionObject = self.registry.protectionObjects[protectedName]
        cmd = GrantStandardSystemAccess(protectionObject)
        cmd.execute()

    def createRefusals(self):
        pass

    def createPersons(self):
        domainName = self.dictionary['domain_name']
        cmd = PersonCreate('admin', 
            role=self.adminRole,
            fullname='Administrator',
            email='kforge-admin@%s' % domainName
        )
        cmd.execute()
        self.adminPerson = cmd.person
        self.adminPerson.setPassword('pass')
        self.adminPerson.save()
        
        visitorRoleName = self.dictionary['visitor_role']
        visitorRole = self.registry.roles[visitorRoleName]
        cmd = PersonCreate(self.dictionary['visitor'],
            role = visitorRole,
            fullname='Visitor',
        )
        cmd.execute()
        self.visitorPerson = cmd.person
        
    def createAccessControlPlugin(self):
        plugins = self.registry.plugins
        plugins.create('accesscontrol')
    
    def createTestPlugins(self):
        plugins = self.registry.plugins
        plugins.create('example')
    
    def setUpTestFixtures(self):
        domainName = self.dictionary['domain_name']
        personRoleName = self.dictionary['person_role']
        personRole = self.registry.roles[personRoleName]
        # do not reuse roles set in other methods as this method
        # should be callable on its own
        adminPerson = self.registry.persons['admin']
        adminRole = self.registry.roles['Administrator']
        friendRole = self.registry.roles['Friend']

        cmd = PersonCreate('levin',
            role = personRole,
            fullname='Levin',
            email='levin@%s' % domainName
        )
        cmd.execute()
        levin = cmd.person
        levin.setPassword('levin')
        levin.save()
        
        cmd = PersonCreate('natasha',
            role = personRole,
            fullname='Natasha',
            email='natasha@%s' % domainName
        )
        cmd.execute()
        natasha = cmd.person
        natasha.setPassword('natasha')
        natasha.save()
        visitor = self.registry.persons[self.dictionary['visitor']]
        
        examplePlugin = self.registry.plugins['example']
    
    def tearDownTestFixtures(self):
        # [[TODO: factor this out into a command class]]
        
        def purgePerson(personName):
            if self.registry.persons.has_key(personName):
                self.registry.persons[personName].delete()
            if self.registry.persons.getAll().has_key(personName):
                self.registry.persons.getAll()[personName].purge()
        purgePerson('natasha')
        purgePerson('levin')
        purgePerson('anna')
        purgePerson('bolskonski')

