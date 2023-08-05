from dm.view.base import AbstractInstanceView
from dm.view.base import AbstractListView
from dm.view.base import AbstractSearchView
from dm.view.base import AbstractCreateView
from dm.view.base import AbstractReadView
from dm.view.base import AbstractUpdateView
from dm.view.base import AbstractDeleteView
from dm.view.manipulator import HasManyManipulator

class RegistryView(AbstractInstanceView):

    domainClassName = ''
    manipulatedFieldNames = {}
    manipulators = {}
    redirectors = {}
    navigation = {}
    registryPathNames = None
    viewPosition = None

    def __init__(self, registryPath=None, actionName='', **kwds):
        super(RegistryView, self).__init__(**kwds)
        self.setRegistryPath(registryPath)
        self.actionName = actionName

    def getRegistryPathNames(self):
        if self.registryPathNames == None:
            if self.registryPath:
                self.registryPathNames = self.registryPath.split('/')
            else:
                self.registryPathNames = []
        return self.registryPathNames

    def countRegistryPathNames(self):
        return len(self.getRegistryPathNames())

    def setRegistryPath(self, registryPath):
        if registryPath != None:
            if registryPath[0] == '/':
                registryPath = registryPath[1:]
            if registryPath[-1] == '/':
                registryPath = registryPath[:-1]
        self.registryPath = registryPath

    def __repr__(self):
        return "<%s redirect='%s' redirectPath='%s' registryPath='%s' actionName='%s'>" % (
            self.__class__.__name__,
            self.redirect,
            self.redirectPath,
            self.registryPath,
            self.actionName,
        )

    def canAccess(self, actionName=None):
        registeredActionName = actionName or self.getAccessControlActionName()
        protectedObject = self.getManipulatedDomainObject()
        if protectedObject == None:
            protectedRegister = self.getManipulatedObjectRegister()
            protectedClassName = protectedRegister.typeName
            protectedClass = self.getDomainClass(protectedClassName)
            protectedObject = protectedClass
        isAuthorised = self.authoriseActionObject(
            registeredActionName, protectedObject
        )
        return isAuthorised

    def canReadDomainObject(self):
        return self.canAccess('Read')

    def canUpdateDomainObject(self):
        return self.canAccess('Update')

    def canDeleteDomainObject(self):
        return self.canAccess('Delete')

    def canCreateDomainObject(self):
        return self.canAccess('Create')

    def getAccessControlActionName(self):
        actionName = self.actionName.capitalize()
        if actionName in ['', 'List', 'Search', 'Find']:
            return 'Read'
        else:
            return actionName

    def makeTemplatePath(self):
        return self.getViewPosition()
        
    def getViewPosition(self):
        if self.viewPosition == None:
            self.viewPosition = ''
            for i in range(0, self.countRegistryPathNames(), 2):
                self.viewPosition += self.getRegistryPathNames()[i] + '/'
            self.viewPosition += self.getTemplatePathActionName()
        return self.viewPosition

    def getTemplatePathActionName(self):
        actionName = self.actionName or "List"
        return actionName[0].lower() + actionName[1:]
        
    def isRegistryPathToRegister(self):
        return self.countRegistryPathNames() % 2
    
    def getManipulatedObjectRegister(self):
        if self.isRegistryPathToRegister():
            registerPathNames = self.getRegistryPathNames()[:]
        else:
            registerPathNames = self.getRegistryPathNames()[:-1]
        owner = self.registry
        register = self.registry
        for name in registerPathNames:
            if owner:
                if not name:
                    raise "Path names error: %s" % str(registerPathNames)
                register = getattr(owner, name)
                owner = None
            else:
                owner = register[name]
        return register

    def getDomainObject(self):
        return self.getRegistryDomainObject()
    
    def getManipulatedDomainObject(self):
        return self.getRegistryDomainObject()
    
    def getRegistryDomainObject(self):
        if self.domainObject == None:
            if not self.isRegistryPathToRegister():
                objectRegister = self.getManipulatedObjectRegister()
                if self.getRegistryPathNames() and objectRegister:
                    registerKey = self.getRegistryPathNames()[-1]
                    self.domainObject = objectRegister[registerKey]
        return self.domainObject

    def setContext(self):
        super(RegistryView, self).setContext()
        if self.isRegistryPathToRegister():
            registerName = self.getRegistryPathNames()[-1]
        else:
            registerName = self.getRegistryPathNames()[-2]
        
        self.context.update({
            'registryPath'  : self.registryPath,
            'registryAttribute'  : self.getRegistryPathNames()[0],
            'registerName' : registerName,
            'registerNameTitle' : registerName[0].capitalize()+registerName[1:],
            'domainClassName' : self.getManipulatedObjectRegister().typeName,
            'actionName'    : self.actionName,
        })

    def getManipulatorClass(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.manipulators:
            manipulatorClass = self.manipulators[viewPosition]
        else:
            manipulatorClass = HasManyManipulator
        return manipulatorClass

    def getManipulatedFieldNames(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.manipulatedFieldNames:
            fieldNames = self.manipulatedFieldNames[viewPosition]
        else:
            fieldNames = []
        return fieldNames

    def getAssociationObject(self): # smell: refused bequest
        return None

    def makePostManipulateLocation(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.redirectors:
            redirectorClass = self.redirectors[viewPosition]
            redirector = redirectorClass(view=self)
            locationPath = redirector.createLocationPath()
        else:
            locationPath = self.defaultPostManipulateLocation()
        return locationPath

    def setMinorNavigationItems(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            self.minorNavigation = navigation.createMinorItems()
        else:
            self.minorNavigation = []

    def getMajorNavigationItem(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            return navigation.createMajorItem()
        else:
            return '/'

    def getMinorNavigationItem(self):
        viewPosition = self.getViewPosition()
        if viewPosition in self.navigation:
            navigationClass = self.navigation[viewPosition]
            navigation = navigationClass(view=self)
            return navigation.createMinorItem()
        else:
            return '/'


class RegistryListView(RegistryView, AbstractListView):
    pass


class RegistrySearchView(RegistryView, AbstractSearchView):

    def searchManipulatedRegister(self):
        register = self.getManipulatedObjectRegister()
        if self.startsWith:
            searchResults = register.startsWith(self.startsWith.capitalize())
        elif self.userQuery:
            searchResults = register.search(self.userQuery)
        resultsList = [i for i in searchResults]
        return resultsList


class RegistryCreateView(RegistryView, AbstractCreateView):

    def setContext(self):
        super(RegistryCreateView, self).setContext()

    def getManipulatedDomainObject(self):
        return None

    def defaultPostManipulateLocation(self):
        locationPath = '/'+ self.registryPath +'/'
        locationPath += str(self.domainObject.getRegisterKeyValue()) +'/'
        return locationPath

    
class RegistryReadView(RegistryListView, AbstractReadView):

    def __init__(self, **kwds):
        super(RegistryReadView, self).__init__(**kwds)
        self.associationObject = None
        
    def getDomainObjectAsNamedValues(self):
        domainObject = self.getDomainObject()
        if not domainObject:
            raise "No domain object for registry path: %s" %self.registryPath
        namedValues = domainObject.asNamedValues()
        manipulator = self.getManipulator()
        filteredNamedValues = []
        if manipulator and manipulator.fieldNames:
            for fieldName in manipulator.fieldNames:
                for namedValue in namedValues:
                    if namedValue['name'] == fieldName:
                        filteredNamedValues.append(namedValue)
        else:
            for namedValue in namedValues:
                metaAttrName = namedValue['name']
                metaAttr = domainObject.meta.attributeNames[metaAttrName]
                if not manipulator.isAttrExcluded(metaAttr):
                    filteredNamedValues.append(namedValue)
        return filteredNamedValues


class RegistryUpdateView(RegistryReadView, AbstractUpdateView):

    def defaultPostManipulateLocation(self):
        return '/' + self.registryPath + '/'


class RegistryDeleteView(RegistryReadView, AbstractDeleteView):

    def defaultPostManipulateLocation(self):
        registryPath = '/'.join(self.getRegistryPathNames()[0:-1])
        return '/' + registryPath + '/'


def view(request, registryPath, actionName=''):
    pathNames = registryPath.split('/')
    if not actionName:
        if len(pathNames) % 2:
            actionName = 'list'
        else:
            actionName = 'read'
    if actionName == 'list':
        viewClass = RegistryListView
    elif actionName == 'create':
        viewClass = RegistryCreateView
    elif actionName == 'read':
        viewClass = RegistryReadView
    elif actionName == 'update':
        viewClass = RegistryUpdateView
    elif actionName == 'delete':
        viewClass = RegistryDeleteView
    elif actionName == 'undelete':
        viewClass = RegistryUndeleteView
    elif actionName == 'purge':
        viewClass = RegisryPurgeView
    else:
        raise "No view class for actionName '%s'." % actionName
    view = viewClass(
        request=request,
        registryPath=registryPath,
        actionName=actionName
    )
    return view.getResponse()

