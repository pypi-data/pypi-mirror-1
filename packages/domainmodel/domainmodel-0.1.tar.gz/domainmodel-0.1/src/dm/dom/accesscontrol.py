from dm.dom.base import *
from dm.ioc import *

class Grant(SimpleObject):
    "Registered granted permission. Associates a Role and a Permission."

#    isConstant  = True
    permission  = HasA('Permission')
    role        = HasA('Role')
    dbName      = 'grants'  # plural table name ('grant' is SQL keyword)

    def getLabelValue(self):
        return "%s-%s" % (
            self.role.getLabelValue(),
            self.permission.getLabelValue(),
        )

class Role(SimpleNamedObject):
    "Registered role."

    isConstant  = True
    grants = HasMany('Grant', 'permission')
    
    def hasPermission(self, permission):
        return permission in self.grants


class Action(SimpleNamedObject):
    """
    Registered action.
    Actions are combined with ProtectionObjects to create Permissions.
    """
    
    isConstant  = True
    # define aggregates
    permissions = AggregatesMany('Permission', 'protectionObject')  
    
    def initialise(self, register):
        super(Action, self).initialise(register)
        # initialise aggregates
        for protectionObject in self.registry.protectionObjects:  
            self.permissions.create(protectionObject)


class Permission(SimpleObject):
    """
    Registered permission. Associates Actions and ProtectionObjects.
    Permissions are combined with Roles and Persons to create Grants and Bars.
    """

#    isConstant  = True
    action           = HasA('Action')
    protectionObject = HasA('ProtectionObject')
    grants           = AggregatesMany('Grant', 'role')
    personalGrants   = AggregatesMany('PersonalGrant', 'person')
    personalBars     = AggregatesMany('PersonalBar', 'person')
    
    def getLabelValue(self):
        return "%s-%s" % (
            self.protectionObject.getLabelValue(),
            self.action.getLabelValue(),
        )


class ProtectionObject(SimpleNamedObject):
    "Protects a protected object with a protected name."

#    isConstant  = True
    permissions = AggregatesMany('Permission', 'action')

    def isProtector(self, protectedObject):
        protectedNames = self.makeProtectedNames(protectedObject)
        return self.name in protectedNames

    def makeProtectedName(self, protectedObject):
        protectedName = ''
        if protectedObject.__class__ == type:
            className = protectedObject.__name__
            protectedName = className
        else:
            className = protectedObject.__class__.__name__
            keyValue = protectedObject.getRegisterKeyValue()
            protectedName = className + "." + str(keyValue)
        return protectedName

    makeProtectedName = classmethod(makeProtectedName)
    
    def makeProtectedNames(self, protectedObject):
        protectedNames = []
        if protectedObject.__class__ == type:
            className = protectedObject.__name__
            protectedNames.append(className)
        else:
            className = protectedObject.__class__.__name__
            keyValue = protectedObject.getRegisterKeyValue()
            protectedNames.append(className + "." + str(keyValue))
            protectedNames.append(className)
        return protectedNames

    makeProtectedNames = classmethod(makeProtectedNames)
    
    def initialise(self, register):
        super(ProtectionObject, self).initialise(register)
        # initialise aggregates 
        for action in self.registry.actions:  
            self.permissions.create(action)

