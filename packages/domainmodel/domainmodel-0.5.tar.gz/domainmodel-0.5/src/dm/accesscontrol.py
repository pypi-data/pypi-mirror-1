from dm.ioc import RequiredFeature
from dm.exceptions import *
from dm.dictionarywords import VISITOR_NAME
from dm.strategy import FindProtectionObjects

moddebug = False

class BaseAccessController(object):
    """Template class for controlling access to protected objects.

    Client objects will call the isAuthorised() method with keywords:
    
        accessController.isAuthorised(
            person=joe,
            actionName='Update',
            protectedObject=joe
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
    registry = RequiredFeature('DomainRegistry')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.action = None
        self.person = None
        self.protectedObject = None
        self.protectionObjects = None
        self.permissions = None
        self.visitor = None
        
    def isAuthorised(self, **kwds):
        singleUseInstance = self.__class__()
        isAuthorised = singleUseInstance.isAccessAuthorised(**kwds)
        return isAuthorised

    def isAccessAuthorised(self, person, actionName, protectedObject):
        self.logAccessAttempt(person, actionName, protectedObject)
        try:
            self.setPerson(person)
            self.setAction(actionName)
            self.setProtectedObject(protectedObject)
            self.assertAccessAuthorised()
        except AccessIsAuthorised, inst:
            if moddebug and self.debug:
                if self.person:
                    personName = self.person.name
                else:
                    personName = 'None'
                self.logger.debug(
                    "Access Authorised: Person '%s' to '%s' object '%s'" % (
                        personName,
                        self.actionName,
                        self.protectedObject,
                    )
                )
            return True
        except AccessNotAuthorised, inst:
            if moddebug and self.debug:
                if self.person:
                    personName = self.person.name
                else:
                    personName = 'None'
                self.logger.debug(
                    "Access Denied: Person '%s' to '%s' object '%s': %s" % (
                        personName, 
                        self.actionName,
                        self.protectedObject,
                        inst,
                    )
                )
        return False

    def logAccessAttempt(self, person, actionName, protectedObject):
        if moddebug and self.debug:
            if person:
                personName = person.name
            else:
                personName = 'None'
            self.logger.debug(
                "Access Request: Person '%s' to '%s' object '%s'." % (
                    personName, actionName, protectedObject,
                )
            )

    def setPerson(self, person):
        self.permissions = None
        if not person:
            self.person = self.getVisitor()
        else:
            self.person = person

    def setAction(self, actionName):
        self.permissions = None
        self.actionName = actionName
        if not actionName:
            raise AccessNotAuthorised("No action name.")
        if self.registry != None:
            self.action = self.registry.actions[self.actionName]
        else:
            self.action = None

    def setProtectedObject(self, protectedObject):
        self.permissions = None
        if not protectedObject:
            raise AccessNotAuthorised("No protected object.")
        self.protectedObject = protectedObject
        self.setProtectionObjects(protectedObject)
        
    def setProtectionObjects(self, protectedObject):
        findObjects = FindProtectionObjects(protectedObject)
        self.protectionObjects = findObjects.find()

    def assertAccessAuthorised(self):
        msg = "Access not authorised on any role and denied by default."
        raise AccessNotAuthorised(msg)

    def isRoleAuthorised(self, role):
        if self.isPermissionGranted(role.grants):
            if moddebug and self.debug:
                msg = "Access authorised by '%s' associated role." % (
                    role.name
                )
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not authorised by '%s' associated role." % (
                    role.name
                )
                self.logger.debug(msg)
            return False

    def isPermissionGranted(self, grants):
        for permission in self.getPermissions():
            if permission in grants:
                return True
        return False

    def getPermissions(self):
        if self.permissions == None:
            self.permissions = []
            for protection in self.protectionObjects:
                permission = protection.permissions[self.action]
                self.permissions.append(permission)
        return self.permissions

    def isPersonNotVisitor(self):
        return self.person != self.getVisitor()

    def getVisitor(self):
        if self.visitor == None:
            if self.registry != None:
                visitorName = self.dictionary[VISITOR_NAME]
                self.visitor = self.registry.persons[visitorName]
            else:
                return None
        return self.visitor


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
            if moddebug and self.debug:
                msg = "Access personally barred."
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not personally barred."
                self.logger.debug(msg)
            return False

    def isVisitorBarred(self):
        if self.isPermissionGranted(self.getVisitor().bars):
            if moddebug and self.debug:
                msg = "Access barred to visitor."
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not barred to visitor."
                self.logger.debug(msg)
            return False

    def isPersonAuthorisedPersonally(self):
        if self.isPermissionGranted(self.person.grants):
            if moddebug and self.debug:
                msg = "Access authorised by personal role."
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not authorised by personal role."
                self.logger.debug(msg)
            return False

    def isVisitorAuthorisedPersonally(self):
        if self.isPermissionGranted(self.getVisitor().grants):
            if moddebug and self.debug:
                msg = "Access authorised by visitor personal role."
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not authorised by visitor personal role."
                self.logger.debug(msg)
            return False
 
    def isPersonAuthorisedOnSystem(self):
        systemRole = self.getPersonSystemRole()
        roleName = getattr(systemRole, 'name', '')
        if self.isPermissionGranted(systemRole.grants):
            if moddebug and self.debug:
                msg = "Access authorised by '%s' system role." % roleName
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not authorised by '%s' system role." % roleName
                self.logger.debug(msg)
            return False

    def isVisitorAuthorisedOnSystem(self):
        systemRole = self.getVisitorSystemRole()
        if self.isPermissionGranted(systemRole.grants):
            if moddebug and self.debug:
                msg = "Access authorised by visitor's system role."
                self.logger.debug(msg)
            return True
        else:
            if moddebug and self.debug:
                msg = "Access not authorised by visitor's system role."
                self.logger.debug(msg)
            return False

    def getPersonSystemRole(self):
        return self.person.role

    def getVisitorSystemRole(self):
        return self.getVisitor().role

