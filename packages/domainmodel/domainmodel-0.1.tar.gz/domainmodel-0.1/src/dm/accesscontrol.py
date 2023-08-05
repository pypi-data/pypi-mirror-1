from dm.ioc import RequiredFeature
from dm.exceptions import *
from dm.dictionarywords import VISITOR_NAME

class BaseAccessController(object):
    """Template class for controlling access to protected objects.

    Client objects will call the isAuthorised() method with keywords:
    
        accessController.isAuthorised(
            person=joe, actionName='Update', protectedObject=joe
        )
    
    Concrete access controllers inheriting this class simply involve
    domain objects holding grants in the access control scheme by
    extending the default assertAccessAuthorised() method.

    Access is denied by raising the AccessNotAuthorised exception in the
    assertAccessAuthorised() method implementation. Likewise, access is
    authorised by raising the AccessIsAuthorised exception within this method.

    To check whether a role's grants include the pertaining permission,
    call the isPermissionGranted() method passing the grants register as
    the only parameter, and test the return value for boolean truth.

    """
    
    dictionary = RequiredFeature('SystemDictionary')
    registry   = RequiredFeature('DomainRegistry')
    logger     = RequiredFeature('Logger')
    debug      = RequiredFeature('Debug')

    def __init__(self):
        self.action           = None
        self.person           = None
        self.permissionObject = None
        self.protectionObject = None
        self.protectedObject  = None
        self.visitor          = None
        
    def isAuthorised(self, **kwds):
        singleUseInstance = self.__class__()
        isAuthorised = singleUseInstance.isAccessAuthorised(**kwds)
        return isAuthorised

    def isAccessAuthorised(self, person, actionName, protectedObject):
        try:
            self.setPerson(person)
            self.setAction(actionName)
            self.setProtectedObject(protectedObject)
            self.assertAccessAuthorised()
        except AccessIsAuthorised, inst:
            if self.debug:
                self.logger.debug(
                    "Access Authorised: Person '%s' to '%s' object '%s'" % (
                        self.person.name,
                        self.actionName,
                        self.protectedObject,
                    )
                )
            return True
        except AccessNotAuthorised, inst:
            self.logger.info(
                "Access Denied: Person '%s' to '%s' object '%s': %s" % (
                    self.person.name, 
                    self.actionName,
                    self.protectedObject,
                    inst,
                )
            )
        return False

    def setPerson(self, person):
        if not person:
            self.person = self.getVisitor()
        else:
            self.person = person

    def setAction(self, actionName):
        self.actionName = actionName
        if not actionName:
            raise AccessNotAuthorised("No action name.")
        self.action = self.registry.actions[self.actionName]

    def setProtectedObject(self, protectedObject):
        if not protectedObject:
            raise AccessNotAuthorised("No protected object.")
        self.protectedObject = protectedObject
        self.makeProtectedNames()
        self.setProtectionObject()

    def assertAccessAuthorised(self):
        raise AccessNotAuthorised("Access not authorised, by default.")

    def getPermissionObject(self):
        if self.permissionObject == None:
            permission = self.protectionObject.permissions[self.action]
            self.permissionObject = permission
        return self.permissionObject

    def isPermissionGranted(self, grants):
        return self.getPermissionObject() in grants

    def isRoleAuthorised(self, role):
        if self.isPermissionGranted(role.grants):
            if self.debug:
                msg = "Access authorised by '%s' role." % role.name
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not authorised by '%s' role." % role.name
                self.logger.debug(msg)
            return False

    def makeProtectedNames(self):
        self.protectedNames = []
        if self.protectedObject.__class__ == type:
            className = self.protectedObject.__name__
            self.protectedNames.append(className)
        else:
            keyValue = self.protectedObject.getRegisterKeyValue()
            className = self.protectedObject.__class__.__name__
            instanceName = className + "." + str(keyValue)
            self.protectedNames.append(instanceName)
            self.protectedNames.append(className)
        if not self.protectedNames:
            raise "No protected names derived from protection object."

    def setProtectionObject(self):
        protectionObjects = self.registry.protectionObjects
        for name in self.protectedNames:
            if name in protectionObjects:
                self.protectionObject = protectionObjects[name]
                return
        raise "No protection object available for %s" % self.protectedNames

    def getVisitor(self):
        if self.visitor == None:
            visitorName = self.dictionary[VISITOR_NAME]
            self.visitor = self.registry.persons[visitorName]
        return self.visitor

    def isPersonNotVisitor(self):
        return self.person.name != self.getVisitor().name


class SystemAccessController(BaseAccessController):
    "Introduces system and personal roles to access controller."

    def assertAccessAuthorised(self):
        if self.isSystemRoleAuthorised():
            raise AccessIsAuthorised
        if self.isPersonalRoleAuthorised():
            raise AccessIsAuthorised
        super(SystemAccessController, self).assertAccessAuthorised()
        
    def isSystemRoleAuthorised(self):
        if self.isPersonAuthorisedOnSystem():
            return True
        if self.isPersonNotVisitor():  # To avoid repetition.
            if self.isVisitorAuthorisedOnSystem():
                return True
        return False

    def isPersonalRoleAuthorised(self):
        if self.isPersonBarred():
            raise AccessNotAuthorised("Access barred to person.")
        if self.isPersonAuthorisedPersonally():
            return True
        if self.isPersonNotVisitor():  # To avoid repetition.
            if self.isVisitorBarred():
                raise AccessNotAuthorised("Access barred to visitor person.")
            if self.isVisitorAuthorisedPersonally():
                return True
        return False

    def isPersonBarred(self):
        if self.isPermissionGranted(self.person.bars):
            if self.debug:
                msg = "Access personally barred."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not personally barred."
                self.logger.debug(msg)
            return False

    def isVisitorBarred(self):
        if self.isPermissionGranted(self.getVisitor().bars):
            if self.debug:
                msg = "Access barred to visitor."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not barred to visitor."
                self.logger.debug(msg)
            return False

    def isPersonAuthorisedPersonally(self):
        if self.isPermissionGranted(self.person.grants):
            if self.debug:
                msg = "Access personally authorised to person."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not personally authorised to person."
                self.logger.debug(msg)
            return False

    def isVisitorAuthorisedPersonally(self):
        if self.isPermissionGranted(self.getVisitor().grants):
            if self.debug:
                msg = "Access personally authorised to visitor."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not personally authorised to visitor."
                self.logger.debug(msg)
            return False
 
    def isPersonAuthorisedOnSystem(self):
        systemRole = self.getPersonSystemRole()
        if self.isPermissionGranted(systemRole.grants):
            if self.debug:
                msg = "Access authorised by person's system role."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not authorised by person's system role."
                self.logger.debug(msg)
            return False

    def isVisitorAuthorisedOnSystem(self):
        systemRole = self.getVisitorSystemRole()
        if self.isPermissionGranted(systemRole.grants):
            if self.debug:
                msg = "Access authorised by visitor's system role."
                self.logger.debug(msg)
            return True
        else:
            if self.debug:
                msg = "Access not authorised by visitor's system role."
                self.logger.debug(msg)
            return False

    def getPersonSystemRole(self):
        return self.person.role

    def getVisitorSystemRole(self):
        return self.getVisitor().role

