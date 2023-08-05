from dm.dom.classregister import DomainClassRegister
from dm.dom.base import *
from dm.dom.stateful import *
from dm.ioc import * 
from dm.exceptions import * 

class DomainRegistry(AbstractList):
    "Holds top-level domain object registers."

    def __init__(self):
        "Initialises top-level domain object registers."
        super(DomainRegistry, self).__init__()
        self.domainClassRegister = None
        self.backgroundObjectCache = []

    def registerCoreDomainClasses(self):
        pass
         
    def loadBackgroundObjects(self):
        "Creates and caches refs to all background domain objects."
        pass
        
    def retrieveItem(self, key):
        return getattr(self, key)

    def createDomainClass(self, metaDomainObject):
        baseClass = DomainObject
        domainClass = metaDomainObject.createDomainClass(baseClass)
        self.registerDomainClass(domainClass)

    def getDomainClassRegister(self):
        if not self.domainClassRegister:
            self.domainClassRegister = DomainClassRegister()
        return self.domainClassRegister

    def isDomainClassRegistered(self, className):
        if className.__class__.__name__ != 'str':
            message = 'className is not a str: %s' % str(className)
            raise Exception(message)
        classRegister = self.getDomainClassRegister()
        return className in classRegister
    
    def getDomainClass(self, className):
        classRegister = self.getDomainClassRegister()
        if not className in classRegister:
            raise "Domain class '%s' is not defined." % className
        return classRegister[className]

    def registerDomainClass(self, domainClass):
        baseClass = DomainObject
        if not issubclass(domainClass, baseClass):
            raise Exception, "Class is not subclass of DomainObject."
        domainClassName = domainClass.__name__
        classRegister = self.getDomainClassRegister()
        if domainClassName in classRegister:
            if features.allowReplace:
                return
            raise "Domain class '%s' is already defined." % domainClassName

        if not 'meta' in domainClass.__dict__ or not domainClass.__dict__['meta']:
            domainClass.meta = domainClass.metaClass(domainClassName)
            
        if not domainClass.meta.dbName:
            if domainClass.dbName:
                domainClass.meta.dbName = domainClass.dbName

        # 'Concrete Table Inheritance', Martin Fowler
        # - http://martinfowler.com/eaaCatalog/concreteTableInheritance.html
        self.setMetaAttributesFromClass(domainClass, domainClass.meta)
        
        domainClass.meta.isUnique = domainClass.isUnique
        domainClass.meta.isCached = domainClass.isConstant
        classRegister[domainClassName] = domainClass
        domainClass.isRegistered = True
        self.createPersistenceClass(domainClass.meta)
        self.setDeferredAttributesOnRegisteredClasses(domainClass)
        for name in classRegister:
            self.checkHasAsForHasManys(classRegister[name])

    def setMetaAttributesFromClass(self, domainClass, domainClassMeta):
        classAttrs = domainClass.__dict__
        className = domainClass.__name__
        for attrName in classAttrs:
            classAttr = classAttrs[attrName]
            if issubclass(classAttr.__class__, MetaDomainAttr):
                defaultInstanceName = className[0].lower() + className[1:]
                if classAttr.typeName == className:
                    if attrName == defaultInstanceName:
                        raise Exception, "Usage of name '%s' for attribute HasA('%s') on '%s' class is not supported. Please use a different attribute name." % (attrName, className, className)
                # fix up 'owner' for lists of associates
                if issubclass(classAttr.__class__, AssociateList):
                    if not classAttr.owner:
                        classAttr.owner = defaultInstanceName
                if issubclass(classAttr.__class__, HasA):
                    if self.isDomainClassRegistered(classAttr.typeName):
                        domainClassMeta.__setattr__(attrName, classAttr)
                    else:
                        domainClassMeta.attributesDeferred[attrName] = classAttr
                elif issubclass(classAttr.__class__, HasMany):
                    if self.isDomainClassRegistered(classAttr.typeName):
                        domainClassMeta.__setattr__(attrName, classAttr)
                    else:
                        domainClassMeta.attributesDeferred[attrName] = classAttr
                else:
                    domainClassMeta.__setattr__(attrName, classAttr)
        for baseClass in domainClass.__bases__:
            if issubclass(baseClass, DomainObject):
                self.setMetaAttributesFromClass(baseClass, domainClassMeta)

    def createPersistenceClass(self, metaDomainObject):
        self.database.createPersistenceClass(metaDomainObject)

    def setDeferredAttributesOnRegisteredClasses(self, domainClass):
        classRegister = self.getDomainClassRegister()
        for className in classRegister:
            registeredClass = classRegister[className]
            deferredAttrs = registeredClass.meta.attributesDeferred
            newAttributes = {}
            for attrName in deferredAttrs:
                    deferredAttr = deferredAttrs[attrName]
                    if issubclass(deferredAttr.__class__, MetaDomainAttr):
                        if ((deferredAttr.typeName == domainClass.__name__) or (deferredAttr.typeName == className)):
                            if issubclass(deferredAttr.__class__, HasA):
                                registeredClass.meta.__setattr__(attrName, deferredAttr)
                                self.addPersistenceAttribute(className, deferredAttr)
                                newAttributes[attrName] = deferredAttr
                            elif issubclass(deferredAttr.__class__, HasMany):
                                registeredClass.meta.__setattr__(attrName, deferredAttr)
                                newAttributes[attrName] = deferredAttr
            for attrName in newAttributes:
                del(deferredAttrs[attrName])

# todo: if domainClass has a HasMany.name == classAttr.owner, then:
#  - create and register a attribute-free join class, 
#  - fixup both HasMany typeNames, 
#  - add HasA attributes to join class for both HasMany attributes. :-)
        
    def checkHasAsForHasManys(self, domainClass):
        for attrName in domainClass.meta.attributeNames:
            domainClassAttr = domainClass.meta.attributeNames[attrName]
            if issubclass(domainClassAttr.__class__, HasMany):
                classRegister = self.getDomainClassRegister()
                if domainClassAttr.typeName in classRegister:
                    registeredClass = classRegister[domainClassAttr.typeName]
                    if domainClassAttr.owner in registeredClass.meta.attributeNames:
                        hasA = registeredClass.meta.attributeNames[domainClassAttr.owner]
                        if not issubclass(hasA.__class__, HasA):
                            raise "Mismatched domain object attribute definitions: HasMany('%s') on class '%s' expected a HasA('%s') called '%s', not '%s'." % (domainClassAttr.typeName, domainClass.__name__, domainClass.__name__, domainClassAttr.owner, hasA.__class__.__name__)
                        if hasA.typeName != domainClass.__name__:
                            raise "Mismatched domain object attribute definitions: HasMany('%s') on class '%s' expected a HasA('%s') called '%s', not HasA('%s')." % (domainClassAttr.typeName, domainClass.__name__, domainClass.__name__, domainClassAttr.owner, hasA.typeName)
                    else:
                        raise "Missing domain object attribute definition: HasMany('%s') on class '%s' expected a HasA('%s') called '%s' on class '%s'. Attribute names are: %s" % (domainClassAttr.typeName, domainClass.__name__, domainClass.__name__, domainClassAttr.owner, domainClassAttr.typeName, registeredClass.meta.attributeNames.keys() )
        
    def addPersistenceAttribute(self, className, attribute):
        self.database.addPersistenceAttribute(className, attribute)

    def loadBackgroundRegister(self, register):
        "Creates and caches refs to given register."
        for key in register.keys():
            object = register[key]
            self.backgroundObjectCache.append(object)

