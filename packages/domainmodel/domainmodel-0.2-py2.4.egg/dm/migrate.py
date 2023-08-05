from dm.ioc import RequiredFeature
from dm.view.manipulator import DomainObjectManipulator
from dm.util.datastructure import MultiValueDict
from dm.exceptions import DataMigrationError
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
import os
import sys
import simplejson

class DomainModelDumper(object):

    def __init__(self):
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")
        self.jsonDataDump = ''
        self.dataDump = None

    def dumpData(self):
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '1')
        self.dataDump = {}
        domainClassRegister = self.registry.getDomainClassRegister()
        for className in domainClassRegister.keys():
            classData = {}
            domainClass = domainClassRegister[className]
            # Dumping class meta data
            metaClassData = {}
            for attr in domainClass.meta.attributes:
                metaClassData[attr.name] = attr.typeName
            classData['metaData'] = metaClassData
            # Dumping class register objects
            domainRegister = domainClass.createRegister()
            for domainObject in domainRegister:
                domainObjectData = domainObject.asDictValues()
                # Dumping object data
                classData[domainObject.id] = domainObjectData
            self.dataDump[className] = classData
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '')
        return self.dataDump

    def dumpDataAsJson(self):
        self.dumpData()
        self.jsonDataDump = simplejson.dumps(self.dataDump)
        return self.jsonDataDump

    def dumpDataToFile(self, dumpFilePath):
        dumpFile = open(dumpFilePath, 'w')
        dumpFileContent = self.dumpDataAsJson()
        dumpFile.write(dumpFileContent)


class DomainModelLoader(object):

    def __init__(self):
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")
        self.jsonDataDump = ''
        self.dataDump = None

    def loadDataFromFile(self, dumpFilePath):
        dumpFile = open(dumpFilePath, 'r')
        dumpFileContent = dumpFile.read()
        self.loadDataAsJson(dumpFileContent)

    def loadDataAsJson(self, jsonDataDump):
        self.jsonDataDump = jsonDataDump
        self.loadData(simplejson.loads(self.jsonDataDump))

    def loadData(self, dataDump):
        self.dataDump = dataDump
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '1')
        self.identifyReferences()
        self.determineImportOrder()
        self.importObjectRecords()
        self.dictionary.set(DB_MIGRATION_IN_PROGRESS, '')

    def identifyReferences(self):
        "Looks for HasA attrs on classes, collects by referenced class."
        
        self.classReferences = {}
        self.outstandingReferences = {}
        
        for className in self.dataDump.keys():
            domainClass = self.registry.getDomainClass(className)
            attrReferences = {}
            for attr in domainClass.meta.attributes:
                if attr.isDomainObjectRef:
                    attrReferences[attr.name] = attr.typeName 
                #elif attr.isAssociateList:
                #    attrReferences[attr.name] = attr.typeName
            self.classReferences[className] = attrReferences
            self.outstandingReferences[className] = attrReferences
                    
    def hasOutstandingReferences(self, className):
        "Checks whether named class references outstanding classes."
        classRefs = self.outstandingReferences[className]
        for attrTypeName in classRefs.values():
            if attrTypeName in self.outstandingReferences:
                return True
        return False
        
    def determineImportOrder(self):
        "Determines import order based on id reference dependencies."
        self.importOrder = []
        
        while(True):
            unreferencingClassName = ''
            unreferencedClassName = ''
            for className in self.outstandingReferences.keys():
                if not self.hasOutstandingReferences(className):
                    unreferencingClassName = className
                    break
            if unreferencingClassName:
                self.importOrder.append(className)
                if className in self.outstandingReferences.keys():
                    del(self.outstandingReferences[className])
                    if not len(self.outstandingReferences):
                        break
                else:
                    msg = "Class name %s not in outstanding list: %s" % (
                        className,
                        self.outstandingReferences.keys()
                    )
                    raise Exception(msg)
            else:
                break
                
                
        if self.outstandingReferences:
            msg = "Classes outstanding when determining import order: %s" % (
                self.outstandingReferences
            )
            raise DataMigrationError(msg)
            
       
    def importObjectRecords(self):
        # Add each object to database
        # substitute ids where changed
        # store new id
        self.idMap = {}
        for className in self.importOrder:
            domainClass = self.registry.getDomainClass(className)
            classRegister = domainClass.createRegister()
            classData = self.dataDump[className]
            #del(self.dataDump[className])
            manipulator = DomainObjectManipulator(classRegister)
            objectIds = classData.keys()
            objectIds.sort()
            #print "Iterating over %s %s" % (className, objectIds)
            for objectId in objectIds:
                objectData = classData[objectId]
                #del(classData[objectId])
                if objectId == 'metaData':
                    continue
                #msg = "Creating %s #%s from %s..." % (
                #    className, objectId, objectData
                #)
                #print msg
                strObjectData = {}
                for attr in domainClass.meta.attributes:
                    if attr.isAssociateList:
                        continue
                    elif attr.isImageFile:
                        continue
                    else:
                        if objectData.has_key(attr.name):
                            value = objectData[attr.name]
                            if attr.isDomainObjectRef and (
                                value.__class__ == int
                            ):
                                idMapKey = "%s %s" % (attr.typeName, value)
                                if idMapKey in self.idMap.keys():
                                    mappedValue = self.idMap[idMapKey]
                                    #msg = "Updating %s %s from %s to %s" % (
                                    #    className,
                                    #    attr.name,
                                    #    value,
                                    #    mappedValue,
                                    #)
                                    value = mappedValue
                            if value.__class__ == unicode:
                                # SQLObject doesn't handle unicode.
                                value = value.encode() 
                            strObjectData[attr.name] = value
                objectDict = MultiValueDict()
                objectDict.update(strObjectData)
                manipulator.create(objectDict)
                domainObject = manipulator.domainObject
                newObjectId = domainObject.id
                if newObjectId != objectId:
                    idMapKey = className +" "+ objectId
                    self.idMap[idMapKey] = newObjectId


class FilesDumper(object):

    def __init__(self):
        self.registry = RequiredFeature("DomainRegistry")
        self.dictionary = RequiredFeature("SystemDictionary")

    def dumpInDir(self, filesDumpDirPath):
        self.filesDumpDirPath = filesDumpDirPath
        self.assertDirExists()

    def assertDirExists(self):
        if not os.path.exists(self.filesDumpDirPath):
            raise Exception("Files dump dir not found: %s" % (
                self.filesDumpDirPath
            ))

