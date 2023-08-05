"""
KForge meta classes describe KForge DomainObject classes.
"""

from dm.ioc import *
import md5
import mx.DateTime
from dm.datetimeconvertor import DateTimeConvertor
from dm.datetimeconvertor import DateConvertor
import Image
from dm.dictionarywords import IMAGES_DIR_PATH
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
import os

class NotDefined(object):
    "Internal 'null' value."
    pass


class MetaBase(object):
    "Domain model meta supertype."

    registry = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    
class MetaDomainObject(MetaBase):
    "Models a domain object."

    reservedAttrNames = ('id', 'record', 'registerCache', 'projectUrls', 'paths', 'pluginController', 'metaClass', 'meta', 'registerKeyName', 'registerClass', 'registry') 

    def __init__(self, name, dbName='', isUnique=True, isCached=False, title='', comment='', isEditable=True, isHidden=False):
        self.name = name          # object class name
        self.dbName = dbName      # object persistent name
        self.attributes = []      # list of meta attribute objects list
        self.attributeNames = {}  # meta attribute objects keyed by name
        self.isUnique = isUnique  # can't create if match exists
        self.isCached = isCached  # hold in memory
        self.title = title        # presentable name
        self.comment = comment    # presentable explanation
        self.isEditable = isEditable
        self.isHidden = isHidden
        if self.isHidden:
            self.isEditable = False
        self.attributesDeferred = {}

    def __setattr__(self, attrName, attrVal):
        if issubclass(attrVal.__class__, MetaDomainAttr):
            if attrName in self.reservedAttrNames:
                raise Exception, "Domain attribute name '%s' is reserved." % attrName
            if not attrName in self.attributeNames:
                attrVal.name = attrName
                self.attributes.append(attrVal)
                self.attributeNames[attrName] = attrVal
        else:
            super(MetaDomainObject, self).__setattr__(attrName, attrVal)

    def createDomainClass(self, baseClass):
        className = self.name
        classAttrs = {'meta': self}
        return self.createClass(className, baseClass, classAttrs)

    def createClass(self, name, base, attrs):
        return type(name, (base,), attrs)

    def hasDeferredAttributes(self):
        return len(self.attributesDeferred) != 0


class MetaDomainAttr(MetaBase):
    "Models a domain object attribute."

    isValueRef = False
    isDomainObjectRef = False
    isAssociateList = False
    isImageFile = False

    def __init__(self, typeName='', name='', dbName='', default=NotDefined, title='', comment='', isEditable=True, isHidden=False, isRequired=True, getChoices=None, **kwds):
        self.typeName = typeName
        self.name = name
        self.dbName = dbName or name
        if default != NotDefined: 
            self.default = default
        self.title = title
        self.comment = comment
        self.isEditable = isEditable
        self.isHidden = isHidden
        if self.isHidden:
            self.isEditable = False
        self.isRequired = isRequired
        self.getChoices = getChoices

    def __repr__(self):
        return "<%s typeName='%s' name='%s'>" % (self.__class__.__name__, self.typeName, self.name)

    def isValueObject(self):
        return False

    def isList(self):
        return False

    def isPaged(self):
        return False

    def isAggregation(self):
        return False

    def isComposition(self):
        return False

    def setInitialValue(self, domainObject):
        initialValue = self.createInitialValue(domainObject)
        if not initialValue == NotDefined:
            setattr(domainObject, self.name, initialValue) 
    
    def createInitialValue(self, domainObject):
        return None

    def createObjectRepr(self, domainObject):
        try:
            valueRepr = self.createValueRepr(domainObject)
        except Exception, inst:
            valueRepr = "!!VALUE_REPR_ERROR: %s!!" % inst
        return "%s=\'%s\'" % (self.name, valueRepr)

    def createValueRepr(self, domainObject):
        value = getattr(domainObject, self.name)
        return str(value)

    def createLabelRepr(self, domainObject):
        return self.createValueRepr(domainObject)

    def createAssociatedNamedValues(self, domainObject):
        raise Exception('No createAssociatedNamedValues method on %s' % self)

    def setAttributeFromMultiValueDict(self, domainObject, multiValueDict):
        try:
            attrValue = self.makeValueFromMultiValueDict(multiValueDict)
        except Exception, inst:
            msg = "Exception making '%s' value from multi-value dict: %s" % (
                self.name, multiValueDict
            )
            self.logger.error(msg)
            raise
        if attrValue != self.getAttributeValue(domainObject):
            msg = "Setting '%s' attribute to '%s'." % (self.name, attrValue)
            self.logger.debug(msg)
            self.setAttributeValue(domainObject, attrValue)

    def makeValueFromMultiValueDict(self, multiValueDict):
        raise Exception, "Abstract method not implemented."

    def setAttributeValue(self, domainObject, attrValue):
        setattr(domainObject, self.name, attrValue)
        
    def getAttributeValue(self, domainObject):
        return getattr(domainObject, self.name)
        
    def getRegistryAttrName(self, domainObject):
        return None

    def setAttributeValueDb(self, domainObject, attrValue):
        self.setAttributeValue(
            domainObject, self.convertFromDbValue(attrValue)
        )
        
    def getAttributeValueDb(self, domainObject):
        return self.convertToDbValue(
            self.getAttributeValue(domainObject)
        )

    def convertFromDbValue(self, dbValue):
        domainValue = dbValue
        return domainValue
        
    def convertToDbValue(self, domainValue):
        dbValue = domainValue
        return dbValue


class ValueObjectAttr(MetaDomainAttr):
    "Models a domain object value attribute."

    isValueRef = True
    isDateTime = False
    isBLOB = False

    def __init__(self, **kwds):
        typeName = self.__class__.__name__
        super(ValueObjectAttr, self).__init__(typeName=typeName, **kwds)

    def isValueObject(self):
        return True 

    def createInitialValue(self, domainObject):
        if hasattr(self, 'default'):
            return self.default
        return NotDefined  # todo: support 'null' default, or forget distinction

    def makeValueFromMultiValueDict(self, multiValueDict):
        return multiValueDict.get(self.name, '')


class String(ValueObjectAttr):
    "Models a domain object string attribute."

    def __init__(self, default='', **kwds):
        super(String, self).__init__(default=default, **kwds)


class Text(String):
    "Models a domain object textual attribute."

    def __init__(self, default='', **kwds):
        super(Text, self).__init__(default=default, **kwds)


class Url(String):
    "Models a domain object url attribute."

    def __init__(self, isRequired=False, **kwds):
        super(Url, self).__init__(isRequired=isRequired, **kwds)


class Password(String):
    "Models a domain object password attribute."

    def __init__(self, isRequired=False, **kwds):
        super(Password, self).__init__(isRequired=isRequired, **kwds)

    def createValueRepr(self, domainObject):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return super(Password, self).createValueRepr(domainObject)
        else:
            return ""

    def makeValueFromMultiValueDict(self, multiValueDict):
        passwordText = multiValueDict[self.name]
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return passwordText
        elif passwordText:
            return self.makeDigest(passwordText)
        else:
            return ''

    def makeDigest(self, clearText):
        return md5.new(clearText).hexdigest()

    def setAttributeValue(self, domainObject, attrValue):
        if attrValue:
            setattr(domainObject, self.name, attrValue)
        

class DateTime(ValueObjectAttr):
    "Models a date-time concern (no timezone)."

    convertor = DateTimeConvertor()
    isDateTime = True

    def __init__(self, default=None, **kwds):
        super(DateTime, self).__init__(default=default, **kwds)

    def makeValueFromMultiValueDict(self, multiValueDict):
        dateTimeString = multiValueDict[self.name]
        return self.convertor.fromHTML(dateTimeString)

    def createValueRepr(self, domainObject):
        dateTimeObject = getattr(domainObject, self.name)
        dateTimeString = self.convertor.toHTML(dateTimeObject)
        return dateTimeString
            

class Date(DateTime):
    "Models a domain object date attribute."
    
    convertor = DateConvertor()


class Boolean(ValueObjectAttr):
    "Models a domain object boolean attribute."

    trueStrings = ['true', 't', '1', 'yes', 'y']

    def __init__(self, default=False, isRequired=False, **kwds):
        super(Boolean, self).__init__(
            default=default, isRequired=isRequired, **kwds
        )

    def makeValueFromMultiValueDict(self, multiValueDict):
        boolVal = multiValueDict[self.name] or False
        if boolVal.__class__ == False.__class__:
            return boolVal
        elif boolVal.__class__ == ''.__class__:
            return boolVal.lower() in self.trueStrings
        else:
            return False

    def createValueRepr(self, domainObject):
        return getattr(domainObject, self.name)


class Integer(ValueObjectAttr):
    "Models a domain object integer attribute."

    def __init__(self, default=0, **kwds):
        super(Integer, self).__init__(default=default, **kwds)

    def makeValueFromMultiValueDict(self, multiValueDict):
        return int(multiValueDict[self.name])


class BLOB(ValueObjectAttr):
    "Models any binary large object attribute."

    isBLOB = True

    def makeValueFromMultiValueDict(self, multiValueDict):
        return multiValueDict[self.name]


class Pickle(BLOB):
    "Models any Python object attribute."

    pass
    

class ImageFile(MetaDomainAttr):
    "Models an image attribute."
    
    isImageFile = True

    def __init__(self, default='', maxWidth=None, **kwds):
        super(ImageFile, self).__init__(default=default, typeName='ImageFile', **kwds)
        self.maxWidth = maxWidth

    def getFileContent(self, mapper):
        filePath = self.getFilepath(mapper)
        if filePath and os.path.exists(filePath):
            file = open(filePath)
            content = file.read()
            file.close()
            return content
        else:
            return None

    def setFileContent(self, mapper, content):
        if mapper:
            filePath = self.getFilepath(mapper)
            if filePath:
                file = open(filePath, 'wb')
                file.write(content)
                file.close()
            if self.maxWidth != None:
                image = Image.open(filePath)
                (width, height) = image.size
                if width > self.maxWidth:
                    widthToHeightRatio = float(width) / height
                    newWidth = self.maxWidth
                    newHeight = newWidth / widthToHeightRatio
                    newSize = (newWidth, newHeight)
                    newImage = image.resize(newSize, Image.ANTIALIAS)
                    newImage.save(filePath)

    def getFilepath(self, mapper):
        # Extn .png doesn't break PIL Image.save() after resize; no extn does.
        fileName = "%s%s.png" % (mapper.__class__.__name__, mapper.id)
        dirPath = self.dictionary[IMAGES_DIR_PATH]
        return os.path.join(dirPath, fileName)


class DomainObjectAssociation(MetaDomainAttr):
    "Associates domain objects with other domain objects."

    def countChoices(self, domainObject):
        if callable(self.getChoices):
            return len(self.getChoices(domainObject))
        else:
            return len(self.getAssociatedObjectRegister(domainObject))

    def getAllChoices(self, domainObject):
        if callable(self.getChoices):
            return self.getChoices(domainObject)
        choices = []
        try:
            associateRegister = self.getAssociatedObjectRegister(domainObject)
            for associateObject in associateRegister.getSortedList():
                key = associateObject.getRegisterKeyValue()
                label = associateObject.getLabelValue()
                choice = (key, label)
                choices.append(choice)
        except Exception, inst:
            message = "Couldn't get choices for %s: %s" % (
               self.typeName, str(inst)
            )
            raise Exception(message)
        return choices

    def getAssociatedObjectRegister(self, domainObject):
        return self.getDomainRegister()

    def getDomainRegister(self):
        domainClass = self.getDomainClass()
        return domainClass.createRegister()

    def getDomainClass(self):
        return self.registry.getDomainClass(self.typeName)
        
    def getObjectByKey(self, key):
        domainRegister = self.getDomainRegister()
        return domainRegister[key]


class DomainObjectRef(DomainObjectAssociation):
    "Associates a domain object with a single aquaintance."

    isDomainObjectRef = True

    def __init__(self, className='', isSimpleOption=False, **kwds):
        self.isSimpleOption = isSimpleOption
        if not className:
            raise Exception, "No className for DomainObjectRef instance."
        super(DomainObjectRef, self).__init__(typeName=className, **kwds)
    
    def getAquaintance(self, domainObject):
        return getattr(domainObject, self.name)
        
    def getRegistryAttrName(self, domainObject):
        aquintanceClass = self.registry.getDomainClass(self.typeName)
        return aquintanceClass.getRegistryAttrName()

    def createInitialValue(self, domainObject):
        if hasattr(self, 'default'):
            if self.default:
                return self.getObjectByKey(self.default)
        return None

    def createValueRepr(self, domainObject):
        value = getattr(domainObject, self.name)
        if value:
            return value.getRegisterKeyValue()
        else:
            return value
       
    def createLabelRepr(self, domainObject):
        value = getattr(domainObject, self.name)
        if value == None:
            return ""
        elif value:
            return str(value.getLabelValue())
        else:
            return str(value)
       
    def makeValueFromMultiValueDict(self, multiValueDict):
        attrValueKey = multiValueDict[self.name]
        if not attrValueKey:
            if hasattr(self, 'default'):
                attrValueKey = self.default
        if not attrValueKey:
            return None
        return self.getObjectByKey(attrValueKey)


class Aggregation(object):
    "Causes deletion of aggregatee by aggregator when aggregator is deleted."

    def isAggregation(self):
        return True


class Composition(Aggregation):
    "Causes creation of aggregatee by aggregator when aggregator is created."

    def isComposition(self):
        return True


class Associate(DomainObjectRef):
    "Models aquaintance with a domain object."
    pass


class Aggregate(Aggregation, Associate):
    "Models aggregation of a domain object."
    pass


class Composite(Composition, Aggregate):
    "Models composition of a domain object."
    pass


class AssociateList(DomainObjectAssociation):
    "Models aquaintance with several domain objects."

    isAssociateList = True
    isPagedList = False
    registerClass = None

    def __init__(self, className='', key='', owner='', isRequired=False, **kwds):
        super(AssociateList, self).__init__(typeName=className, isRequired=isRequired, **kwds)
        self.key = key
        self.owner = owner
    
    def isList(self):
        return True

    def countChoices(self, domainObject):
        associateRegister = self.getAssociatedObjectRegister(domainObject)
        return len(associateRegister)

    def getAllChoices(self, domainObject):
        choices = []
        associateRegister = self.getAssociatedObjectRegister(domainObject)
        objectList = []
        if associateRegister != []:
            objectList = associateRegister.getSortedList()
        for associateObject in objectList:
            key = associateRegister.getRegisterKey(associateObject)
            if self.isKeyDomainObject():
                label = associateObject.getLabelValue()
            else:
                label = key
            choice = (key, label)
            choices.append(choice)
        return choices

    def createInitialValue(self, domainObject):
        className = self.typeName
        recordClass = self.registry.getDomainClass(className)
        registerClass = recordClass.registerClass
        register = registerClass(
            typeName=self.typeName,
            keyName=self.key,
            ownerName=self.owner,
            owner=domainObject
        )
        return register

    def createValueRepr(self, domainObject):
        valuesList = []
        register = self.getAssociationObjectRegister(domainObject)
        if register == None:
            return valuesList
        if self.isKeyDomainObject():
            valuesList = [i.getRegisterKeyValue() for i in register.keys()]
        else:
            valuesList = [i for i in register.keys()]
        return valuesList

    def createLabelRepr(self, domainObject):
        register = self.getAssociationObjectRegister(domainObject)
        labelsList = []
        if self.isKeyDomainObject():
            labelsList = [str(register.getRegisterKey(i).getLabelValue()) for i in register.getSortedList()]
            labelsList = ", ".join(labelsList)
        else:
            labelsList = [str(i.getLabelValue()) for i in register.getSortedList()]
            labelsList = ", ".join(labelsList)
        return labelsList or "_"

    def createValueLabelList(self, domainObject):
        register = self.getAssociationObjectRegister(domainObject)
        valueLabels = []
        isKeyDomainObject = self.isKeyDomainObject()
        for domainObject in register.getSortedList():
            registerKey = register.getRegisterKey(domainObject)
            valueLabel = {}
            if isKeyDomainObject:
                value = registerKey.getRegisterKeyValue() 
                label = str(registerKey.getLabelValue())
            else:
                value = registerKey
                label = str(domainObject.getLabelValue())
            valueLabel['value'] = value
            valueLabel['label'] = label
            valueLabel['associationObject'] = register[registerKey]
            valueLabels.append(valueLabel)
        return valueLabels

    def createAssociatedNamedValues(self, domainObject):
        associatedNamedValues = []
        associationRegister = self.getAssociationObjectRegister(domainObject)
        if self.isKeyDomainObject():  # not bomb proof, really
            for associatedObject in associationRegister.keys():
                namedValue = {}
                keyValue = associatedObject.getRegisterKeyValue() 
                namedValue['key'] = keyValue
                labelValue = str(associatedObject.getLabelValue())
                namedValue['label'] = labelValue
                namedValue['associatedObject'] = associatedObject
                namedValue['associationObject'] = associationRegister[associatedObject]
                associatedNamedValues.append(namedValue)
        else:
            for associatedObject in associationRegister:
                namedValue = {}
                keyValue = associatedObject.getRegisterKeyValue() 
                namedValue['key'] = keyValue
                labelValue = str(associatedObject.getLabelValue())
                namedValue['label'] = labelValue
                namedValue['associatedObject'] = associatedObject
                namedValue['associationObject'] = associatedObject
                associatedNamedValues.append(namedValue)
        return associatedNamedValues

    def setAttributeFromMultiValueDict(self, domainObject, multiValueDict):
        associatedObjectKeys = multiValueDict.getlist(self.name)
        associatedObjectRegister = self.getAssociatedObjectRegister(
            domainObject)
        associationObjectRegister = self.getAssociationObjectRegister(
            domainObject)
        # delete where surplus
        for associationObject in associationObjectRegister:
            associatedObjectKey = getattr(associationObject, self.key)
            if self.isKeyDomainObject():
                associatedObjectKey = associatedObjectKey.getRegisterKeyValue()
            if not str(associatedObjectKey) in associatedObjectKeys:
                associationObject.delete()
        # create where missing
        for associatedObjectKey in associatedObjectKeys:
            if associatedObjectKey == None:
                continue
            if self.isKeyDomainObject():
                associatedObjectKey = associatedObjectRegister[associatedObjectKey]
            if not associatedObjectKey in associationObjectRegister:
                associationObjectRegister.create(associatedObjectKey)

    def getAssociationObjectRegister(self, domainObject):
        return getattr(domainObject, self.name)
        
    def isKeyDomainObject(self):
        if self.key == 'id':
            return False
        keyAttr = self.getKeyMetaAttribute()
        return keyAttr.isDomainObjectRef
        
    def getKeyMetaAttribute(self):
        domainClass = self.getDomainClass()
        if self.key in domainClass.meta.attributeNames:
            return domainClass.meta.attributeNames[self.key]
        else:
            msg = "For class '%s', key '%s' not in attributes: %s." % (
                domainClass.meta.name,
                self.key,
                domainClass.meta.attributeNames.keys(),
            )
            raise Exception(msg)
        
    def getAssociatedObjectRegister(self, domainObject):
        associateRegister = None
        if self.isKeyDomainObject():
            keyMeta = self.getKeyMetaAttribute()
            associateClassName = keyMeta.typeName
            associateClass = self.registry.getDomainClass(associateClassName)
            associateRegister = associateClass.createRegister()
        else:
            if domainObject:
                associateRegister = getattr(domainObject, self.name)
            else:
                associateRegister = []
        return associateRegister   

    def getAssociationObject(self, domainObject, keyValue):
        register = self.getAssociationObjectRegister(domainObject)
        if self.isKeyDomainObject():
            keyMeta = self.getKeyMetaAttribute()
            associateClassName = keyMeta.typeName
            associateClass = self.registry.getDomainClass(associateClassName)
            associateRegister = associateClass.createRegister()
            keyValue = associateRegister[keyValue]
        associationObject = register[keyValue]
        return associationObject

class HasA(Associate):
    "Models aquaintance with a domain object."
    pass


class HasMany(AssociateList):
    "Models aquaintance with several domain objects."
    pass


class AggregatesMany(Aggregation, HasMany):
    "Models aggregation of several domain objects."
    pass


