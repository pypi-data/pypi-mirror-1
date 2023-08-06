from dm.ioc import *

class ModelBuilder(object):

    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')

    def construct(self):
        if self.registry != None:
            self.loadState()
            self.loadSystem()
            self.loadImage()
            self.loadPlugin()
            self.loadAccessControl()
            self.loadPerson()
            self.loadPersonalAccessControl()
            self.loadSession()
            self.loadCaptcha()

    def loadState(self):
        from dm.dom.state import State
        self.registry.registerDomainClass(State)
        self.registry.states = State.createRegister()
        self.registry.loadBackgroundRegister(self.registry.states)

    def loadSystem(self):
        from dm.dom.system import System
        self.registry.registerDomainClass(System)
        self.registry.systems = System.createRegister()

    def loadImage(self):
        from dm.dom.image import Image
        self.registry.registerDomainClass(Image)
        self.registry.images = Image.createRegister()

    def loadPlugin(self):
        from dm.dom.plugin import Plugin
        self.registry.registerDomainClass(Plugin)
        self.registry.plugins = Plugin.createRegister()

    def loadAccessControl(self):
        from dm.dom.accesscontrol import Grant
        self.registry.registerDomainClass(Grant)
        from dm.dom.accesscontrol import Role
        self.registry.registerDomainClass(Role)
        from dm.dom.accesscontrol import Action
        self.registry.registerDomainClass(Action)
        from dm.dom.accesscontrol import Permission
        self.registry.registerDomainClass(Permission)
        from dm.dom.accesscontrol import ProtectionObject
        self.registry.registerDomainClass(ProtectionObject)

        self.registry.grants = Grant.createRegister()
        self.registry.roles = Role.createRegister()
        self.registry.actions = Action.createRegister()
        self.registry.permissions = Permission.createRegister()
        self.registry.protectionObjects = ProtectionObject.createRegister()

        self.registry.loadBackgroundRegister(self.registry.roles)
        self.registry.loadBackgroundRegister(self.registry.actions)

    def loadPerson(self):
        from dm.dom.person import Person
        self.registry.registerDomainClass(Person)
        self.registry.persons = Person.createRegister()

    def loadPersonalAccessControl(self):
        from dm.dom.person import PersonalGrant
        self.registry.registerDomainClass(PersonalGrant)
        from dm.dom.person import PersonalBar
        self.registry.registerDomainClass(PersonalBar)

    def loadSession(self):
        from dm.dom.session import Session
        self.registry.registerDomainClass(Session)
        self.registry.sessions = Session.createRegister()

    def loadCaptcha(self):
        if self.dictionary['captcha.enable']:
            from dm.dom.captcha import Captcha
            self.registry.registerDomainClass(Captcha)
            self.registry.captchas = Captcha.createRegister()

