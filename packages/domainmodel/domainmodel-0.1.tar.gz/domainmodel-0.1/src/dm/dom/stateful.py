from dm.dom.base import *
from dm.dom.meta import *
import dm.exceptions  # todo: remove?
import mx.DateTime

class StatefulRegister(DomainObjectRegister):

    isStateful = True

    def __init__(self, typeName, **kwds):
        super(StatefulRegister, self).__init__(typeName, **kwds)
        self.initialiseWithState = None
        self.requiredState = None
        self.initialiseWithStateName = 'active'
        self.requiredStateName = 'active'

    def coerceKwds(self, kwds):
        super(StatefulRegister, self).coerceKwds(kwds)
        if not kwds.has_key('state'):
            state = self.getRequiredState()
            if state:
                kwds['state'] = state

    def initialiseObject(self, object):
        super(StatefulRegister, self).initialiseObject(object)
        if not object.state:
            object.state = self.getInitialiseWithState()
            object.isChanged = True

    def getRequiredState(self):
        if not self.requiredStateName:
            return None
        if not self.requiredState:
            stateName = self.requiredStateName
            self.requiredState = self.getState(stateName)
        return self.requiredState

    def getInitialiseWithState(self):
        if not self.initialiseWithState:
            stateName = self.requiredStateName or self.initialiseWithStateName
            self.initialiseWithState = self.getState(stateName)
        return self.initialiseWithState

    def getState(self, name):
        return self.registry.states[name]


class CompoundRegister(StatefulRegister):

    def __init__(self, typeName, isCompoundingRegister=True, **kwds):
        super(CompoundRegister, self).__init__(typeName, **kwds)
        if isCompoundingRegister:
            registerClass = self.__class__
            self.deleted = registerClass(typeName, isCompoundingRegister=False, **kwds)
            self.deleted.requiredStateName = 'deleted'
            self.all = registerClass(typeName, isCompoundingRegister=False, **kwds)
            self.all.requiredStateName = ''


class StatefulObject(DomainObject):

    registerClass = CompoundRegister
    state = HasA('State', default='active')

    def __init__(self):
        super(StatefulObject, self).__init__()
        
    def delete(self):
        if self.state:
            self.state.deleteObject(self)
        else:
            super(StatefulObject, self).delete()

    def undelete(self):
        if self.state:
            self.state.undeleteObject(self)

    def purge(self):
        if self.state:
            self.state.purgeObject(self)

#    def raiseUndelete(self):
#        "Raises onUndelete event."
#        self.onUndelete()
#
#    def raisePurge(self):
#        "Raises onPurge event."
#        self.onPurge()
#
#    def onUndelete(self):
#        "Abstract handler for Undelete object event."
#        self.notifyPlugins(self.__class__.__name__ + 'Undelete', self)
#    
#    def onPurge(self):
#        "Abstract handler for Purge object event."
#        self.notifyPlugins(self.__class__.__name__ + 'Purge', self)
#

class NamedStatefulObject(StatefulObject, SimpleNamedObject):
    pass


class SimpleDatedObject(SimpleObject):

    dateCreated = DateTime(default=mx.DateTime.now, isEditable=False)


class SimpleNamedDatedObject(SimpleNamedObject, SimpleDatedObject):
    pass


class DatedStatefulObject(StatefulObject, SimpleDatedObject):
    pass


class NamedDatedStatefulObject(DatedStatefulObject, SimpleNamedObject):
    pass


class StandardObject(NamedDatedStatefulObject):
    pass
    

class PagedCompoundRegister(CompoundRegister):

    isPagedList = True
    
    def __init__(self, typeName, keyName="", pageName="",pageKeys=None,**kwds):
        super(PagedCompoundRegister, self).__init__(
            typeName, keyName=keyName, **kwds
        )
        self.pageName = pageName
        self.pageKeys = pageKeys

    def __iter__(self, **kwds):
        "Returns iterator for project services."
        return iter(self.makeList(**kwds))

    def __len__(self, **kwds):
        "Returns iterator for project services."
        return len(self.makeList(**kwds))

    def __repr__(self):
        className = self.__class__.__name__
        typeName = self.typeName
        keyName = self.keyName
        pageName = self.pageName
        return "<%s typeName=\"%s\" keyName=\"%s\" pageName=\"%s\">" % (
            className, typeName, keyName, pageName
        )

    def has_key(self, page, key):
        return key in self.retrieveItem(page)

    def get(self, page, key, default=None):
        return self.retrieveItem(page).get(key, default)

    def create(self, page, key):
        return self.retrieveItem(page).create(key)

    def makeList(self, **kwds):
        list = []
        for pageKey in self.keys():
            page = self.retrieveItem(pageKey)
            for item in page:
                list.append(item)
        return list

    def coerceKwds(self, kwds):
        raise "Intermediate register isn't a proper domain object register."

    #def getKeyName(self):
    #    raise "Intermediate register isn't a proper domain object register."

    def keys(self):
        if not self.pageKeys:
            raise "No pageKeys method to get pageKeys register."
        pageKeyRegister = self.pageKeys()
        if not pageKeyRegister:
            raise "No page key register."
        return [pageKey for pageKey in pageKeyRegister]
        
    def retrieveItem(self, key):
        item = StatefulRegister(
            self.typeName,
            ownerName=self.ownerName,
            owner=self.owner,
            ownerName2=self.pageName,
            owner2=key,
            keyName=self.keyName,
        )
        item.requiredStateName = self.requiredStateName
        return item


class Paged(MetaDomainAttr):

    isPagedList = True
    
    def isPaged(self):
        return True

    def createInitialValue(self, domainObject):
        registerClass = self.registerClass
        register = registerClass(
            typeName  = self.typeName,
            keyName   = self.key,
            pageName  = self.page,
            pageKeys  = self.pageKeys,
            ownerName = self.owner,
            owner     = domainObject,
        )
        return register

 
class PagedAssociateList(Paged, AssociateList):

    registerClass = PagedCompoundRegister

    def __init__(self, className, key, page, pageKeys=None, **kwds):
        super(PagedAssociateList, self).__init__(className, key, **kwds)
        self.page = page
        self.pageKeys = pageKeys

    def countChoices(self, domainObject):
        associateRegister = self.getAssociatedObjectRegister(domainObject)
        return len(associateRegister)

    def getAllChoices(self, domainObject):
        choices = []
        associateRegister = self.getAssociatedObjectRegister(domainObject)
        if associateRegister:
            for pageKey in associateRegister.keys():
                pageRegister = associateRegister[pageKey]
                for associateObject in pageRegister:
                    if self.isPageKeyDomainObject():
                        key = pageKey.getRegisterKeyValue() 
                        label = pageKey.getRegisterKeyValue()
                    else:
                        key = pageKey
                        label = pageKey
                    key += "::"
                    label += "::"
                    key += associateRegister.getRegisterKey(associateObject)
                    label += associateRegister.getRegisterKey(associateObject)
                  
                    choice = (str(key), str(label))
                    choices.append(choice)
        return choices

    def isPageKeyDomainObject(self):
        pageKeyAttr = self.getPageKeyMetaAttribute()
        return pageKeyAttr.isDomainObjectRef

    def getPageKeyMetaAttribute(self):
        domainClass = self.getDomainClass()
        return domainClass.meta.attributeNames[self.page]

    def createValueRepr(self, domainObject):
        valueList = []
        for (key, label) in self.getAllChoices(domainObject):
            valueList.append(key)
        return valueList

    def createLabelRepr(self, domainObject):
        labelList = []
        for (key, label) in self.getAllChoices(domainObject):
            labelList.append(label)
        return ", ".join(labelList) or "_"

    def createValueLabelList(self, domainObject):
        valueLabels = []
        for (value, label) in self.getAllChoices(domainObject):
            valueLabel = {}
            valueLabel['value'] = value
            valueLabel['label'] = label
            valueLabels.append(valueLabel)
        return valueLabels

    def getAssociationObject(self, domainObject, keyValue):
        keyValues = keyValue.split('::')
        if len(keyValues) != 2:
            raise "Only one page key allowed: %s" % keyValues
        pageKeyValue = keyValues[0]
        objectKeyValue = keyValues[1]

        pageKey = None
        if self.isPageKeyDomainObject():
            pageKeyMeta = self.getPageKeyMetaAttribute()
            pageKeyClassName = pageKeyMeta.typeName
            pageKeyClass = self.registry.getDomainClass(pageKeyClassName)
            pageKeyRegister = pageKeyClass.createRegister()
            pageKey = pageKeyRegister[pageKeyValue]
        else:
            pageKey = pageKeyValue
        
        objectKey = None
        if self.isKeyDomainObject():
            objectKeyMeta = self.getKeyMetaAttribute()
            objectKeyClassName = objectKeyMeta.typeName
            objectKeyClass = self.registry.getDomainClass(objectKeyClassName)
            objectKeyRegister = objectKeyClass.createRegister()
            objectKey = associatedRegister[objectKeyValue]
        else:
            objectKey = objectKeyValue
            
        pagedRegister = self.getAssociatedObjectRegister(domainObject)
        registerPage = pagedRegister[pageKey]
        associationObject = registerPage[objectKey]
        return associationObject

    def setAttributeFromMultiValueDict(self, domainObject, multiValueDict):
        associatedObjectKeys = multiValueDict.getlist(self.name)

        # todo: split keys by "::", get domain model values from strings,
        #       then run over paged register, deleting and then creating
#        raise str(associatedObjectKeys)
#        associatedObjectRegister = self.getAssociatedObjectRegister(domainObject
#)
#        associationObjectRegister = getattr(domainObject, self.name)
#        # delete where surplus
#        for associationObject in associationObjectRegister:
#            associatedObjectKey = getattr(associationObject, self.key)
#            if self.isKeyDomainObject():
#                associatedObjectKey = associatedObjectKey.getRegisterKeyValue()
#            if not associatedObjectKey in associatedObjectKeys:
#                associationObject.delete()
#        # create where missing
#        for associatedObjectKey in associatedObjectKeys:
#            if self.isKeyDomainObject():
#                associatedObjectKey = associatedObjectRegister[associatedObjectK
#ey]
#            if not associatedObjectKey in associationObjectRegister:
#                associationObjectRegister.create(associatedObjectKey)



class PagedAggregateList(Aggregation, PagedAssociateList):
    pass


class PagedCompositeList(Composition, PagedAssociateList):
    pass


class HasManyPages(PagedAssociateList):
    pass


# todo: problem of not being able to use HasManyPages without StatefulObjects:
# todo: create PagedRegister in core.dom.base, and pagedRegisterClass on DomainObject, overridden on StatefulDomainObject - or use the domain object class?

