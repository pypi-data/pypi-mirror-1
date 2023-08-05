from dm.ioc import *
from dm.dom.meta import *

from dm.exceptions import *

debug = RequiredFeature('Debug')

class DomainBase(object):
    """
    'Layer Supertype (475)'  [Fowler, 2003]
    """

    log              = RequiredFeature('Logger')
    dictionary       = RequiredFeature('SystemDictionary')
    registry         = RequiredFeature('DomainRegistry')
    pluginController = RequiredFeature('PluginController')


class AbstractList(DomainBase):
    """
    Supertype for domain model registers.
    Follows 'AbstractList' in 'Iterator (257)' [GoF].
    """ 

    database = RequiredFeature('DatabaseFacade')

    def __init__(self, 
        owner=None, ownerName=None, owner2=None, 
        ownerName2=None, isCached=False, **kwds
    ):
        self.owner = owner
        self.ownerName = ownerName
        self.owner2 = owner2
        self.ownerName2 = ownerName2
        self.isCached = isCached
        if self.isCached:
            self.cache = dict()
        else:
            self.cache = None

    def __contains__(self, key):
        "Supports: if key in register:"
        return self.has_key(key)

    def __getitem__(self, key):
        "Supports: item = register[key]"
        item = self.find(key)
        return item

    def get(self, key, default=None):
        "Implements: register[key] if key in register, else default (None)."
        try:
            return self.__getitem__(key)
        except:
            return default
                
    def has_key(self, key):
        "Tests existence of register entity with key."
        if self.isCached:
            if key in self.cache:
                return True
        try:
            item = self.find(key)
        except:
            return False
        else:
            return True
       
    def find(self, key):
        "Returns keyed object."
        if self.isCached:
            if key in self.cache:
                if debug:
                    message = 'Cache hit for key: %s' % key
                    self.log.debug(message)
                return self.readCache(key)
            else:
                if debug:
                    message = 'Cache miss for key: %s' % key
                    self.log.debug(message)
        if debug:
            message = 'Retrieving record for key: %s' % key
            self.log.debug(message)
        return self.retrieveItem(key)

    def retrieveItem(self, *args, **kwds):
        "Abstract method to retrieve register entity."
        return None

    def beginTransaction(self):
        "Begins a transaction."
        return self.database.beginTransaction()
        

class RegisterIterator(object):
    "Iterator for domain object registers."

    def __init__(self, **kwds):
        self.results  = iter(kwds['results'])
        self.register = kwds['register']

    def next(self):
        nextRecord = self.results.next()
        return nextRecord.getDomainObject()

    def __getitem__(self, key):
        itemRecord = self.results[key]
        return itemRecord.getDomainObject()

    def __iter__(self):
        return self


class DomainObjectRegister(AbstractList):
    "Supertype for concrete domain object registers."

    isStateful = False

    def __init__(self, typeName='', keyName='id', **kwds):
        super(DomainObjectRegister, self).__init__(**kwds)
        self.typeName = typeName
        self.keyName = keyName
        if 'searchAttributeNames' in kwds:
            self.searchAttributeNames = kwds['searchAttributeNames']
        else:
            self.searchAttributeNames = ''
        if 'startsWithAttributeName' in kwds:
            self.startsWithAttributeName = kwds['startsWithAttributeName']
        else:
            self.startsWithAttributeName = ''
        
    def __repr__(self):
        className = self.__class__.__name__
        typeName = self.typeName
        keyName = self.keyName
        return "<%s typeName='%s' keyName='%s'>" % (
            className, typeName, keyName
        )

    def retrieveItem(self, key):
        "Attempts to retrieve existing domain object from database."
        item = None
        try:
            item = self.findDomainObject(key)
            if item and self.isCached:
                self.cacheItem(item)
            if not item:
                message = "findDomainObject() returned: %s" % str(item)
                raise StandardError(message)
        except StandardError, inst:
            msg = "No %s called '%s' found: %s" \
                % (self.typeName, key, inst)
            raise KforgeRegistryKeyError, msg
        return item

    def create(self, *args, **kwds):
        "Returns new registered domain object."
        item = self.createDomainObject(*args, **kwds)
        if item:
            if self.isCached:
                self.cacheItem(item)
            item.raiseCreate()
        return item

    def __len__(self):
        "Supports: len(registry)"
        return self.count()
        #return self.database.countRecords(self.typeName)

    def __iter__(self, **kwds):
        "Returns iterator for registered items."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        results = self.database.listRecords(self.typeName, **kwds)
        iter = RegisterIterator(results=results, register=self)
        return iter
 
    def __delitem__(self, key):
        "Supports: del registry[key]"
        item = self[key]
        item.delete()
        
    def count(self, **kwds):
        "Returns count of matching records."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.countRecords(self.typeName, **kwds)
    
    def keys(self, **kwds):
        "Returns list of keys for registry."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        keys = []
        results = self.database.listRecords(self.typeName, **kwds)
        keyName = self.getKeyName()
        for record in results:
            key = getattr(record.getDomainObject(), keyName)
            keys.append(key)
        return keys
    
    def startsWith(self, value, attributeName=''):
        kwds = {}
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        if not attributeName:
            attributeName = self.getStartsWithAttributeName()
        results = self.database.startsWith(
            self.typeName, value, attributeName, **kwds
        )
        iter = RegisterIterator(results=results, register=self)
        return iter
    
    def search(self, userQuery, attributeNames=None):
        kwds = {}
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        if not attributeNames:
            attributeNames = self.getSearchAttributeNames()
        results = self.database.search(
            self.typeName, userQuery, attributeNames, **kwds
        )
        iter = RegisterIterator(results=results, register=self)
        return iter
    
    def createDomainObject(self, *args, **kwds):
        try:
            self.coerceArgs(args, kwds)
            self.initialiseKwds(kwds)
            self.initialiseWithDefaults(kwds)
            self.coerceKwds(kwds)
            self.switchToRecords(kwds)
            object = self.database.createDomainObject(self.typeName, **kwds)
            self.initialiseObject(object)
            if object.isChanged:
                object.save()
        except KforgeDbError, inst:
            raise KforgeDomError, inst 
        else:
            return object

    def findDomainObject(self, key):
        "Finds existing object."
        kwds = dict()
        keyName = self.getKeyName()
        if keyName: 
            kwds[keyName] = key
            record = self.findRecord(**kwds)
            return record.getDomainObject()
        else:
            raise "No keyName set on %s" % self

    def read(self, *args, **kwds):
        self.coerceArgs(args, kwds)
        record = self.findRecord(**kwds)
        return record.getDomainObject()
            
    def findDomainObjects(self, **kwds):
        return [r.getDomainObject() for r in self.findRecords(**kwds)]
    
    def findRecord(self, **kwds):
        "Finds existing object record."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.findRecord(self.typeName, **kwds)

    def findRecords(self, **kwds):
        "Finds existing object records."
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        return self.database.findRecords(self.typeName, **kwds)

    def coerceArgs(self, args, kwds):
        "Sets registryKey from args if not registryKey in kwds."
        keyName = self.getKeyName()
        if not kwds.has_key(keyName):
            if len(args):
                kwds[keyName] = args[0]

    def getDomainClass(self):
        return self.registry.getDomainClass(self.typeName)

    def getDomainClassMeta(self):
        domainClass = self.getDomainClass()
        return domainClass.meta
    
    def getDomainClassMetaAttributes(self):
        domainClassMeta = self.getDomainClassMeta()
        return domainClassMeta.attributes
    
    def getDomainClassMetaAttributeNames(self):
        domainClassMeta = self.getDomainClassMeta()
        return domainClassMeta.attributeNames
    
    def initialiseKwds(self, kwds):
        pass
        
    def initialiseWithDefaults(self, kwds):
        for metaAttr in self.getDomainClassMetaAttributes():
            attrName = metaAttr.name
            if attrName in kwds:
                continue
            if metaAttr.isDomainObjectRef:
                if not (hasattr(metaAttr, 'default') and metaAttr.default):
                    continue
                attrClassName = metaAttr.typeName
                attrClass = self.registry.getDomainClass(attrClassName)
                attrDomainRegister = attrClass.createRegister()
                attrValue = attrDomainRegister[metaAttr.default]
                kwds[attrName] = attrValue

    def coerceKwds(self, kwds):
        if self.owner and self.ownerName:
            kwds[self.ownerName] = self.owner
        if self.owner2 and self.ownerName2:
            kwds[self.ownerName2] = self.owner2
        if self.keyName and self.keyName in kwds:
            keyValue = kwds[self.keyName]
            if issubclass(keyValue.__class__, DomainObject):
                kwds[self.keyName] = keyValue

    def switchToRecords(self, kwds):
        metaAttributeNames = self.getDomainClassMetaAttributeNames()
        for attrName in kwds.keys():
            if attrName in metaAttributeNames:
                metaAttr = metaAttributeNames[attrName]
                if metaAttr.isDomainObjectRef:
                    domainObject = kwds[attrName]
                    if domainObject:
                        if hasattr(domainObject, 'record'):
                            kwds[attrName] = domainObject.record
                        else:
                            msg = "No record for '%s' domainObjectRef: %s" % (
                                attrName, kwds
                            )
                            raise msg
                
    def initialiseObject(self, object):
        object.initialise(self)

    def cacheItem(self, item):
        "Adds item to in-memory cache."
        key = self.getRegisterKey(item)
        self.cache[key] = item
        item.cacheRegister(self)
    
    def readCache(self, item):
        "Reads item from in-memory cache."
        return self.cache[item]
    
    def decacheItem(self, item):
        "Removes item from in-memory cache."
        item.decacheRegister(self)
        key = self.getRegisterKey(item)
        self.decacheKey(key)
    
    def decacheKey(self, key):
        "Removes key from in-memory cache."
        del self.cache[key]
    
    def getRegisterKey(self, domainObject):
        "Returns key for domain object in register."
        attrName = self.getKeyName()
        return getattr(domainObject, attrName)
   
    # todo: clear this up - aren't class attributes enough?
    def getKeyName(self):
        "Returns name of domain object attribute used for register key."
        if hasattr(self, 'keyName'):
            if self.keyName:  
                return self.keyName
        else:
            return 'id'

    def getStartsWithAttributeName(self):
        "Returns name of domain object attribute used in alphabetical index."
        return self.startsWithAttributeName or self.getKeyName()

    def getSearchAttributeNames(self):
        "Returns name of attributes used for searching domain objects'."
        return self.searchAttributeNames or [self.getStartsWithAttributeName()]


class Register(DomainObjectRegister):
    pass


class DomainObject(DomainBase):
    """
    Domain object supertype. Follows 'Domain Model (116)'. 
    """

    registerKeyName = 'id'
    registerClass = Register
    meta = None
    metaClass = MetaDomainObject
    paths = RequiredFeature('FileSystem') 
    isConstant = False
    isUnique = True
    searchAttributeNames = []
    isRegistered = False
    dbName = ''
    registryAttrName = None

    def __init__(self, **kwds):
        "Initialise base attributes."
        self.assertIsClassRegistered()
        self.isChanged = False
        self.registerCache = {}
        self.record = None
        self.id = None
        if self.meta:
            for metaAttr in self.meta.attributes:
                metaAttr.setInitialValue(self)
                
    def __repr__(self):
        attrsRepr = "" 
        if self.meta:
            for attr in self.meta.attributes:
                if attr.isValueRef:
                    attrsRepr += " " + attr.createObjectRepr(self)
        className = self.__class__.__name__
        return "<%s id='%s'%s>" % (className, str(self.id), attrsRepr)

    def asNamedValues(self, excludeName=''):
        namedValues = [] 
        if self.meta:
            for attr in self.meta.attributes:
                if not excludeName == attr.name:
                    namedValue = {}
                    namedValue['name'] = attr.name
                    namedValue['value'] = attr.createValueRepr(self)
                    namedValue['label'] = attr.createLabelRepr(self)
                    namedValue['domainKeyValue'] = self.getRegisterKeyValue()
                    namedValue['isDomainObjectRef'] = attr.isDomainObjectRef
                    namedValue['registryAttrName'] = attr.getRegistryAttrName(self)
                    namedValue['typeName'] = attr.typeName
                    namedValue['isAssociateList'] = attr.isAssociateList
                    namedValues.append(namedValue)
        return namedValues

    def asDictValues(self):
        dictValues = {} 
        if self.meta:
            for attr in self.meta.attributes:
                dictValues[attr.name] = attr.createValueRepr(self)
        return dictValues

    def asDictLabels(self):
        labels = {} 
        if self.meta:
            for attr in self.meta.attributes:
                labels[attr.name] = attr.createLabelRepr(self)
        return labels

    def assertIsClassRegistered(self):
        className = self.__class__.__name__
        if not self.isClassRegistered(self.__class__):
            message = "Class '%s' is not registered." % className
            raise DomainClassRegistrationError(message)
        if not self.meta:
            message = "Class '%s' has no meta object." % className
            raise DomainClassRegistrationError(message)
        if len(self.meta.attributesDeferred):
            message = "Class '%s' has mismatched attributes: %s" % (
                className, str(self.meta.attributesDeferred))
            raise DomainClassRegistrationError(message)

    def isClassRegistered(self, domainClass):
        return domainClass.isRegistered

    def initialise(self, register=None):
        pass 
    
    def save(self):
        "Update record of object in the database."
        self.record.saveDomainObject()
        self.raiseUpdate()
        
    def delete(self):
        self.deleteAggregates()
        self.raiseDelete()
        self.destroySelf()

    def deleteAggregates(self):
        for metaAttr in self.meta.attributes:
            if metaAttr.isAggregation():
                if metaAttr.isList():
                    self.deleteAggregateList(metaAttr.name)

    def deleteAggregateList(self, attrName):
        aggregateRegister = getattr(self, attrName)
        for aggregateObject in aggregateRegister:
            aggregateObject.delete()

    def destroySelf(self):
        "Destroy record of object in the database."
        self.decacheItem()
        if self.record:
            self.record.domainObject = None
            self.record.destroySelf()
            self.record = None

    def purgeAggregates(self):
        for metaAttr in self.meta.attributes:
            if metaAttr.isAggregation():
                if metaAttr.isList():
                    self.purgeAggregateList(metaAttr.name)

    def purgeAggregateList(self, attrName):
        aggregateRegister = getattr(self, attrName)
        for aggregateObject in aggregateRegister:
            aggregateObject.purge()

    def decacheItem(self):
        for register in self.registerCache.keys():
            register.decacheItem(self)

    def notifyPlugins(self, *args):
        if self.pluginController:
            self.pluginController.notify(*args)

    def raiseCreate(self):
        "Raises onCreate event."
        self.onCreate()
        message = "Created %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)

    def raiseUpdate(self):
        "Raises onUpdate event."
        self.onUpdate()

    def raiseDelete(self):
        "Raises onDelete event."
        self.onDelete()
        message = "Deleted %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)

    def raiseUndelete(self):
        "Raises onUndelete event."
        self.onUndelete()
        message = "Undeleted %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)

    def raisePurge(self):
        "Raises onDelete event."
        self.onPurge()

    def onCreate(self):
        "Abstract handler for Create object event."
        self.notifyPlugins(self.__class__.__name__ + 'Create', self)

    def onUpdate(self):
        "Abstract handler for Update event."
        self.notifyPlugins(self.__class__.__name__ + 'Update', self)

    def onDelete(self):
        "Abstract handler for Delete object event."
        self.notifyPlugins(self.__class__.__name__ + 'Delete', self)
    
    def onUndelete(self):
        "Abstract handler for Undelete object event."
        self.notifyPlugins(self.__class__.__name__ + 'Undelete', self)
    
    def onPurge(self):
        "Abstract handler for Purge object event."
        self.notifyPlugins(self.__class__.__name__ + 'Purge', self)

    def cacheRegister(self, register):
        "Remember a register."
        self.registerCache[register] = register

    def decacheRegister(self, register):
        "Forget a register."
        if register in self.registerCache:
            del(self.registerCache[register])

    def createRegister(self, **kwds):
        if not ('typeName' in kwds and kwds['typeName']):
            kwds['typeName'] = self.__name__
        if not ('keyName' in kwds and kwds['keyName']):
            kwds['keyName']  = self.registerKeyName
        if not ('isCached' in kwds and kwds['isCached']):
            kwds['isCached'] = self.isConstant
        if not ('searchAttributeNames' in kwds and kwds['searchAttributeNames']):
            kwds['searchAttributeNames'] = self.searchAttributeNames
        if debug:
            className = self.registerClass.__name__
            message = "Creating '%s' register with kwds: %s" % (className, kwds)
            self.log.debug(message)
        register = self.registerClass(**kwds)
        return register
        
    createRegister = classmethod(createRegister)
    
    def getRegisterKeyValue(self):
        "Returns register key for domain object."
        return getattr(self, self.registerKeyName)
  
    def getRegistryAttrName(self):
        if not self.registryAttrName:
            self.registryAttrName = self.createCollectiveNoun()
        return self.registryAttrName

    getRegistryAttrName = classmethod(getRegistryAttrName)
    
    def getRegistryId(self):
        return "%s.%s" % (
            self.getRegistryAttrName(),
            self.getRegisterKeyValue(),
        )
    
    # todo: rename to getLabel
    def getLabelValue(self):
        return self.getRegisterKeyValue()

    def getPersonalLabel(self):
        return self.getRegisterKeyValue()

    def createCollectiveNoun(self):
        noun = self.createNoun()
        # caution: naive pluralisation ahead!
        if noun[-1] == 'y':
            noun = noun[:-1] + 'ies'
        elif noun[-1] == 's':
            noun = noun[:-1] + 'ses'
        else:
            noun = noun + 's'
        return noun

    createCollectiveNoun = classmethod(createCollectiveNoun)
    
    def createNoun(self):
        name = self.__name__
        return name[0].lower() + name[1:]
        
    createNoun = classmethod(createNoun)


class SimpleObject(DomainObject):
    pass
    
    
class SimpleNamedObject(DomainObject):

    registerKeyName = 'name'
    name = String()

