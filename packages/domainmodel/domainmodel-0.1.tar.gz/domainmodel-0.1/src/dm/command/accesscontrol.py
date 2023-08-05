from dm.command import Command
from dm.exceptions import *

class AccessControlCommand(Command):
    "Abstract role-based access control command."
        
    def __init__(self, role=None, actionName=None, protectedObject=None):
        super(AccessControlCommand, self).__init__(
            role=role,
            actionName=actionName,
            protectedObject=protectedObject
        )
        self.role = role
        self.actionName = actionName
        self.protectedObject = protectedObject
        self.grant = None

    def execute(self):
        super(AccessControlCommand, self).execute()
        self.validateInput()

    def validateInput(self):
        if not self.role:
            raise KforgeCommandError("No role.")
        if not self.actionName:
            raise KforgeCommandError("No action name.")
        else:
            self.action = self.registry.actions[self.actionName]
        if not self.protectedObject:
            raise KforgeCommandError("No protectedObject.")

    def findGrant(self):
        for grant in self.role.grants:
            permission = grant.permission
            if permission.action == self.action:
                protectionObject = permission.protectionObject
                if protectionObject.isProtector(self.protectedObject):
                    self.grant = grant
                    return True
        return False


class GrantAccess(AccessControlCommand):
    "Grants permission for a role to take an action with an object."

    def execute(self):
        super(GrantAccess, self).execute()
        
        # todo: if instance, then find instance po, not 'maybe class po'.
        #       - this will require move makeProtectedName methods elsewhere
        
        for protectionObject in self.registry.protectionObjects:
            if protectionObject.isProtector(self.protectedObject):
                permission = protectionObject.permissions[self.action]
                if not permission in self.role.grants:
                    self.role.grants.create(permission)
                return True
        error = "Could not grant permission on role '%s' to '%s' object '%s'." % (self.role.name, self.action.name, self.protectedObject)
        self.raiseError(error)


class RevokeAccess(AccessControlCommand):
    "Grants permission for a role to take an action with an object."

    def execute(self):
        super(RevokeAccess, self).execute()
        if self.findGrant():
            self.grant.delete()
        else:
            error = "No grant on role '%s' to '%s' object '%s'." % (
                self.role.name, self.action.name, self.protectedObject
            )
            self.raiseError(error)


class GrantStandardSystemAccess(Command):
    """
    Grants profile of permissions for roles to take actions with an object.
    """

    def __init__(self, protectionObject):
        super(GrantStandardSystemAccess, self).__init__()
        self.protectionObject = protectionObject
        self.read = self.findPermission('Read')

    def execute(self):
        self.createGrants()

    def createGrants(self):

        # Administrator allowed everything.
        
        administrator = self.registry.roles['Administrator']
        for permission in self.protectionObject.permissions:
            if not permission in administrator.grants:
                administrator.grants.create(permission)

        # Developer allowed to read.
        
        developer = self.registry.roles['Developer']
        developer.grants.create(self.read)

        # Friend allowed to read.
        
        friend = self.registry.roles['Friend']
        friend.grants.create(self.read)

        # Visitor allowed to read
        visitor = self.registry.roles['Visitor']
        visitor.grants.create(self.read)
        
    def findPermission(self, actionName):
        action = self.registry.actions[actionName]
        return self.protectionObject.permissions[action]

    def grantAccess(self, role, actionName):
        cmd = GrantAccess(role, actionName, self.protectedObject)
        cmd.execute()


class GrantStandardDevelopmentAccess(GrantStandardSystemAccess):

    def __init__(self, protectionObject):
        super(GrantStandardDevelopmentAccess, self).__init__(protectionObject)
        self.update = self.findPermission('Update')

    def execute(self):
        self.createGrants()

    def createGrants(self):
        super(GrantStandardDevelopmentAccess, self).createGrants()
        
        # Developer allowed to update.
        
        developer = self.registry.roles['Developer']
        developer.grants.create(self.update)
        
        # Visitor not allowed to read so remove grants from inherited from
        # GrantStandardSystemAccess
        visitor = self.registry.roles['Visitor']
        visitor.grants[self.read].delete()


class GrantStandardProjectAccess(GrantStandardDevelopmentAccess):

    pass

