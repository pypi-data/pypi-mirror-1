"""System exception classes."""

# todo: Rename Kforge out of this module.

class DmException(StandardError):
    "System exception super class."
    pass

class AccessControlException(DmException):
    pass

class AccessIsAuthorised(AccessControlException):
    pass

class AccessNotAuthorised(AccessControlException):
    pass

class KforgeError(StandardError):
    "Kforge exception superclass."
    pass

class KforgeAbstractMethodError(KforgeError):
    "Unimplemented abstract method exception class."
    pass

class KforgeCommandError(KforgeError):
    "Command exception class."
    pass

class KforgePersonActionObjectDeclined(KforgeCommandError):
    "Access control denied class."
    pass
    
class KforgeRegistryKeyError(KforgeError, KeyError):
    "Registry exception class."
    pass
    
class KforgeSessionCookieValueError(KforgeError):
    "Session cookie exception class."
    pass
    
class KforgeDomError(KforgeError):
    "Domain layer exception class."
    pass

class DomainClassRegistrationError(KforgeDomError):
    "Domain class registration exception class."
    pass
    
class KforgeDbError(KforgeError):
    "Database layer exception class."
    pass

class KforgePluginMethodNotImplementedError(KforgeAbstractMethodError):
    "Missing plugin method exception class."
    pass

class KforgeMissingPluginSystemClass(KforgeError):
    "Missing plugin class exception class."

