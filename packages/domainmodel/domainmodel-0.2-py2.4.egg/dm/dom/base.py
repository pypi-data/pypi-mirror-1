from dm.ioc import *
from dm.dom.meta import *
from dm.exceptions import *
import dm.times
from dm.util.datastructure import MultiValueDict

debug = RequiredFeature('Debug')
domdebug = False

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
                if domdebug and debug:
                    message = "Cache hit for key: '%s'" % key
                    self.log.debug(message)
                return self.readCache(key)
            else:
                if domdebug and debug:
                    message = "Cache miss for key: '%s'" % key
                    self.log.debug(message)
        if domdebug and debug:
            message = "Retrieving from %s record for key: '%s'" % (self, key)
            if message == 'WeekEarmarkTemplate':
                raise Exception, message
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
        #return RegisterIterator(results=results, register=self)
        iterator = RegisterIterator(results=results, register=self)
        objectList = [i for i in iterator]
        self.sortDomainObjects(objectList)
        return objectList
    
    def search(self, userQuery, attributeNames=None):
        kwds = {}
        self.coerceKwds(kwds)
        self.switchToRecords(kwds)
        if not attributeNames:
            attributeNames = self.getSearchAttributeNames()
        results = self.database.search(
            self.typeName, userQuery, attributeNames, **kwds
        )
        iterator = RegisterIterator(results=results, register=self)
        objectList = [i for i in iterator]
        self.sortDomainObjects(objectList)
        return objectList
    
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
            raise Exception, "No keyName set on %s" % self

    def read(self, *args, **kwds):  # todo: rename to something better
        self.coerceArgs(args, kwds)
        record = self.findRecord(**kwds)
        return record.getDomainObject()
            
    def findSingleDomainObject(self, **kwds):
        return self.findFirstDomainObject(**kwds)

    def findFirstDomainObject(self, **kwds):
        domainObjects = self.findDomainObjects(**kwds)
        if len(domainObjects) >= 1:
            return domainObjects[0]
        else:
            return None
    
    def findLastDomainObject(self, **kwds):
        domainObjects = self.findDomainObjects(**kwds)
        if len(domainObjects) >= 1:
            return domainObjects[-1]
        else:
            return None
    
    def findDomainObjects(self, **kwds):
        objectList = []
        for record in self.findRecords(**kwds):
            domainObject = record.getDomainObject()
            objectList.append(domainObject)
        self.sortDomainObjects(objectList)
        return objectList
    
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
# Just speculating that the following lines are useless. - johnbywater
#        if self.keyName and self.keyName in kwds:
#            keyValue = kwds[self.keyName]
#            if issubclass(keyValue.__class__, DomainObject):
#                kwds[self.keyName] = keyValue

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
                            raise Exception, msg
                
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
   
    def getKeyName(self):
        "Returns name of domain object attribute used for register key."
        if hasattr(self, 'keyName') and self.keyName:
            keyName = self.keyName
        else:
            keyName = 'id'
        return keyName

    def getStartsWithAttributeName(self):
        "Returns name of domain object attribute used in alphabetical index."
        return self.startsWithAttributeName or self.getKeyName()

    def getSearchAttributeNames(self):
        "Returns name of attributes used for searching domain objects'."
        return self.searchAttributeNames or [self.getStartsWithAttributeName()]

    def getObjectList(self):
        objectList = [domainObject for domainObject in self]
        return objectList
    
    def getSortedList(self):
        objectList = self.getObjectList()
        self.sortDomainObjects(objectList)
        return objectList

    def sortDomainObjects(self, domainObjects):
        if debug:
            msg = "Sorting domain object list (len %s)." % len(domainObjects)
            self.log.debug(msg)
        domainObjects.sort(self.cmpDomainObjects)

    def cmpDomainObjects(self, x, y):
        xValue = x.getSortOnValue()
        yValue = y.getSortOnValue()
        sortAscending = x.sortAscending
        if xValue < yValue:
            if sortAscending:
                return -1
            else:
                return 1
        if xValue == yValue:
            return 0
        if xValue > yValue:
            if sortAscending:
                return 1
            else:
                return -1

    def getNextObject(self, objectList, domainObject):
        if domainObject not in objectList:
            return None
            #msg = "Object not in list: %s %s" % (domainObject, objectList)
            #raise Exception(msg)
        index = objectList.index(domainObject)
        index += 1
        if (index < len(objectList)):
            return objectList[index]
        else:
            return None

    def getPreviousObject(self, objectList, domainObject):
        if domainObject not in objectList:
            return None
            #msg = "Object not in list: %s %s" % (domainObject, objectList)
            #raise Exception(msg)
        index = objectList.index(domainObject)
        index -= 1
        if (index >= 0):
            return objectList[index]
        else:
            return None


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
    startsWithAttributeName = ''
    isRegistered = False
    dbName = ''
    registryAttrName = None
    sortOnName = None 
    sortAscending = True

    def __init__(self, **kwds):
        "Initialise base attributes."
        #self.objectAttrValues = {}    # experimental
        self.assertIsClassRegistered()
        self.isChanged = False
        self.registerCache = {}
        self.record = None
        self.id = None
        if self.meta:
            for metaAttr in self.meta.attributes:
                metaAttr.setInitialValue(self)
                
    ## experimental
    #def __setattr__(self, attrName, attrVal):
    #    if self.meta and self.meta.attributeNames.has_key(attrName) and hasattr(self, 'objectAttrValues'):
    #        self.objectAttrValues[attrName] = attrVal
    #    else:
    #        super(DomainObject, self).__setattr__(attrName, attrVal)
    #    #super(DomainObject, self).__setattr__(attrName, attrVal)
   
    ## experimental
    #def __getattr__(self, attrName):
    #    raise AttributeError(attrName)
    #    if self.meta and self.meta.attributeNames.has_key(attrName) and hasattr(self, 'objectAttrValues'):
    #        return self.objectAttrValues.get(attrName, None)
    #    else:
    #        raise AttributeError(attrName)

    def __repr__(self):
        className = self.__class__.__name__
        reprAttrs = self.reprAttrs()
        return "<%s %s>" % (className, reprAttrs)

    def reprAttrs(self):
        reprAttrs = ' id=%d' % self.id
        if self.meta:
            for attr in self.meta.attributes:
                if attr.isValueRef and not attr.isBLOB:
                    reprAttrs += ' %s' % attr.createObjectRepr(self)
                elif attr.isDomainObjectRef:
                    reprAttrs += ' %s' % attr.createObjectRepr(self)
        return reprAttrs


    def getSortOnValue(self):
        if self.sortOnName:
            return getattr(self, self.sortOnName)
        else:
            return self.getPersonalLabel()

    def asNamedValues(self, excludeName=''):  # todo: excludeNames
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
                    if attr.isDomainObjectRef:
                        namedValue['isSimpleOption'] = attr.isSimpleOption
                    else:
                        namedValue['isSimpleOption'] = False
                    namedValue['registryAttrName'] = attr.getRegistryAttrName(self)
                    namedValue['typeName'] = attr.typeName
                    namedValue['isAssociateList'] = attr.isAssociateList
                    if attr.isAssociateList:
                        namedValue['associatedNamedValues'] = attr.createAssociatedNamedValues(self)
                    namedValues.append(namedValue)
        return namedValues

    def asDictValues(self):
        dictValues = {} 
        if self.meta:
            for attr in self.meta.attributes:
                dictValues[attr.name] = attr.createValueRepr(self)
        return dictValues

    def asRequestParams(self):
        requestParams = MultiValueDict()
        for attr in self.meta.attributes:
            attrName = attr.name
            attrValueRepr = attr.createValueRepr(self)
            if attr.isList():
                requestParams.setlist(attrName, attrValueRepr)
            else:
                if attrValueRepr != None:
                    requestParams[attrName] = attrValueRepr
                else:
                    requestParams[attrName] = ''
        return requestParams

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
        self.saveSilently()
        self.raiseUpdate()

    def saveSilently(self):
        "Update record without raising update event."
        self.updateLastModifiedTime()
        self.record.saveDomainObject()

    def updateLastModifiedTime(self):
        if 'lastModified' in self.meta.attributeNames:
            self.lastModified = dm.times.getUniversalNow()
        
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
        if debug:
            message = "Updated %s: '%s'" % (
                self.__class__.__name__,
                self
            )
            self.log.debug(message)

    def raiseDelete(self):
        "Raises onDelete event."
        self.onDelete()
        message = "Deleted %s: '%s'" % (
            self.__class__.__name__,
            self.getRegisterKeyValue()
        )
        self.log.info(message)

    def raiseApprove(self):
        "Raises onApprove event."
        self.onApprove()
        message = "Approved %s: '%s'" % (
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
        "Raises onPurge event."
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
    
    def onApprove(self):
        "Abstract handler for Approve object event."
        self.notifyPlugins(self.__class__.__name__ + 'Approve', self)
    
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
        if not('searchAttributeNames' in kwds and kwds['searchAttributeNames']):
            kwds['searchAttributeNames'] = self.searchAttributeNames
        if not('startsWithAttributeName' in kwds and kwds['startsWithAttributeName']):
            kwds['startsWithAttributeName'] = self.startsWithAttributeName
        if domdebug and debug:
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
        # default to register key value
        return self.getRegisterKeyValue()

    def getPersonalLabel(self):
        # default to basic label
        return self.getLabelValue()

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

