"""KForge Data Mapper. Follows 'Data Mapper (165)', [Fowler, 2003]
    
This module provides relational database persistence to the Domain Model.

It is responsible for moving data between domain model objects and database
objects. SQLObject is used as an object-relational mapper to move data
between database objects and a relational database management system.

This module works by using domain model meta data objects to construct data
mapper meta data objects, which then control SQLObject classes. A database
facade presents methods for defining data mappers, and for creating and
retrieving records from the relational database.

This module avoids collisions of domain model names with database keywords,
and translates between names of the domain model and names of the database.
It also provides various features for making selections from the domain model,
such as after-before intervals for times, and search for text attributes.


    # create facade
    import dm.db
    db = dm.db.DatabaseFacade()

    # define mapper class
    db.createMapperClass(metaDomainObject)

    # create records
    project = db.createRecord('Project', name='projekt')
    person = db.createRecord('Person', name='joe')
    member = db.createRecord('Member', project=project, person=person)

    # read records
    project = db.findRecord('Project', name='projekt')
    person = db.findRecord('Person', name='joe')
    member = db.findRecord('Member', project=project, person=person)
"""

from sqlobject import *
from sqlobject.converters import sqlrepr
from dm.ioc import *
import dm.dom.meta
from dm.exceptions import KforgeDbError
import sqlobject.main
from dm.ioc import *
from dictionarywords import *

debug = RequiredFeature('Debug')
logger = RequiredFeature('Logger')

class ConnectionFacade(object):
    "Presents database connection."

    dictionary = RequiredFeature('SystemDictionary')

    def __init__(self):
        dbType = self.dictionary[DB_TYPE]
        dbUser = self.dictionary[DB_USER]
        dbPass = self.dictionary[DB_PASS]
        dbHost = self.dictionary[DB_HOST]
        dbName = self.dictionary[DB_NAME]
        uri = "%s://%s:%s@%s/%s" % (dbType, dbUser, dbPass, dbHost, dbName)
        try:
            self.connection = connectionForURI(uri)
            self.connection.makeConnection()
        except Exception, inst:
            msg = 'Could not connect to database: %s' % (inst)
            logger.critical(msg)
            raise msg
        if debug:
            logger.debug('Connected to database OK.')
    
    def getConnection(self):
        return self.connection
    
    def beginTransaction(self):
        "Begin a new transaction."
        return self.connection.transaction()


class DatabaseFacade(object):
    "Presents database records."
    
    class __singletonDatabaseFacade(object):

        hasMapperClasses = False
        mappers = {}

        def __init__(self):
            "Initialises ConnectionFacade composite."
            self.connection = ConnectionFacade()
        
        def getConnection(self):
            return self.connection.getConnection()
        
        def beginTransaction(self):
            "Begin a transaction."
            return self.connection.beginTransaction()

        def findRecord(self, className, *args, **kwds):
            "Retreive record of domain object."
            record = None
            if self.isSelectById(kwds) and len(kwds) == 1:
                record = self.get(className, kwds['id'])
            else:
                records = self.findRecords(className, **kwds)
                if hasattr(records, 'count'):
                    if records.count():
                        record = records[0]
                    else:
                        msg = "Can't find %s record with params %s %s." \
                            % (className, args, kwds)
                        raise KforgeDbError, msg
                else:
                    record = records
            if debug:
                logger.debug('Found %s record from database.' % (className))
            return record
        
        def isSelectById(self, kwds):
            if 'id' in kwds:
                return True
            return False

        def isSelectByTimeInterval(self, kwds):
            if '__startsAfter__' in kwds:
                return True
            if '__startsBefore__' in kwds:
                return True
            if '__endsAfter__' in kwds:
                return True
            if '__endsBefore__' in kwds:
                return True
            return False

        def get(self, className, id):
            "Retreive record of domain object."
            recordClass = self.getRecordClass(className)
            return recordClass.get(id)

        def findRecords(self, className, *args, **kwds):
            "Retreive records of domain objects."
            recordClass = self.getRecordClass(className)
            if self.isSelectById(kwds):
                records = recordClass.selectByKeywordsWithId(**kwds)
            elif self.isSelectByTimeInterval(kwds):
                records = recordClass.selectByKeywordsWithTimeInterval(**kwds)
            else:    
                records = recordClass.selectByKeywords(**kwds)
            return records

        def startsWith(self, className, value, attributeName, **kwds):
            recordClass = self.getRecordClass(className)
            return recordClass.startsWith(value, attributeName, **kwds)

        def search(self, className, userQuery, attributeNames, **kwds):
            recordClass = self.getRecordClass(className)
            return recordClass.search(userQuery, attributeNames, **kwds)

        def countRecords(self, className, *args, **kwds):
            "Counts recorded domain objects."
            list = self.listRecords(className, *args, **kwds)
            return list.count()
       
        def listRecords(self, className, *args, **kwds):
            "Returns list of recorded domain objects."
            if kwds:
                records = self.findRecords(className, *args, **kwds)
            else:
                records = self.getRecordClass(className).select()
            if debug:
                logger.debug('Listed %s records from database.' % (className))
            return records
       
        def createDomainObject(self, className, *args, **kwds):
            "Create new recorded domain object."
            newRecord = self.createRecord(className, *args, **kwds)
            if debug:
                message = "Created new db record. %s" % newRecord
                logger.debug(message)
            newObject = newRecord.getDomainObject()
            return newObject
          
        def createRecord(self, className, *args, **kwds):
            "Create record of domain object."
            recordClass = self.getRecordClass(className)
            recordClass.assertCreateParams(*args, **kwds)
            try:
                newRecord = recordClass(*args, **kwds)
            except Exception, inst:
                msg = "Can't create new %s record with params %s: %s"  \
                    % (className, kwds, inst)
                raise KforgeDbError, msg 
            else:
                return newRecord
       
        def getRecordClass(self, className):
            "Returns record class for domain object type name."
            if not className: 
                raise "Can't get record class without class name."
            try:
                mapperClass = self.mappers[className]
            except Exception, inst:
                raise "Mapper class '%s' not defined in: %s. (%s)" % (
                    className,
                    str(self.mappers),
                    str(inst)
                )
            else:
                return mapperClass

        getRecordClass = classmethod(getRecordClass)
        
        def createMapperClass(self, metaDomainObject):
            baseClass = dm.db.Mapper
            className = metaDomainObject.name
            if className not in self.mappers:
                metaMapper = MetaMapper(metaDomainObject)
                mapperClass = metaMapper.createMapperClass(baseClass)
                self.mappers[className] = mapperClass
                self.checkMapperClassTable(className)
            elif not features.allowReplace:
                raise "Mapper for '%s' already defined." % className

        createMapperClass = classmethod(createMapperClass)

        def createPersistenceClass(self, metaDomainObject):
            self.createMapperClass(metaDomainObject)

        createPersistenceClass = classmethod(createPersistenceClass)

        def checkMapperClassTable(self, className):
            mapperClass = self.getRecordClass(className)
            try:
                mapperClass.select().count()
            except:
                try:
                    mapperClass.createTable()
                except: 
                    raise 
                else: 
                    mapperClass.select().count()
                    msg = "Added %s table in database." % (
                        mapperClass.meta.dbName
                    )
                    logger.info(msg)
            return 1
            
        checkMapperClassTable = classmethod(checkMapperClassTable)

        def addPersistenceAttribute(self, className, domAttribute):
            mapperClass = self.getRecordClass(className)
            mapperAttribute = mapperClass.meta.addAttribute(domAttribute)
            sqlAttribute = mapperAttribute.createNamedMapperClassAttribute()
            if hasattr(mapperClass.sqlmeta, 'addColumn'):   # for SQLObject 0.7
                addColumn = mapperClass.sqlmeta.addColumn
                delColumn = mapperClass.sqlmeta.delColumn
            else:                                           # for SQLObject 0.6
                addColumn = mapperClass.addColumn
                delColumn = mapperClass.delColumn
            try:    
                addColumn(sqlAttribute, changeSchema=False)
            except:
                if features.allowReplace:
                    return
                raise
            try:
                list(mapperClass.select())
            except:
                delColumn(sqlAttribute, changeSchema=False)
                addColumn(sqlAttribute, changeSchema=True)
                list(mapperClass.select())
                msg = "Added %s field to %s table in database." % (
                    mapperAttribute.dbName,
                    mapperClass.meta.dbName
                )
                logger.info(msg)

    __instance = __singletonDatabaseFacade()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class ReservedNames(object):

    reservedNames = None
    dictionary = RequiredFeature('SystemDictionary')
    sqlKeywords = {
        'common': [
            'ABSOLUTE', 'ADD', 'ADMIN', 'AFTER',
            'AND', 'ANY', 'ARE', 'ARRAY', 'AS',
            'ASC', 'ASSERTION', 'AT', 'AUTHORIZATION', 'BEFORE',
            'BEGIN', 'BINARY', 'BIT', 'BLOB', 'BOOLEAN',
            'BOTH', 'BREADTH', 'BY', 'CALL', 'CASCADE',
            'CASCADED', 'CASE', 'CAST', 'CATALOG', 'CHAR',
            'CHARACTER', 'CHECK', 'CLASS', 'CLOB', 'CLOSE',
            'COLLATE', 'COLLATION', 'COLUMN', 'COMMIT', 'COMPLETION',
            'CONNECT', 'CONNECTION', 'CONSTRAINT', 'CONSTRAINTS',
            'CONSTRUCTOR', 'CONTINUE', 'CORRESPONDING', 'CREATE', 'CROSS',
            'CUBE', 'CURRENT', 'CURRENT_DATE', 'CURRENT_PATH', 'CURRENT_ROLE',
            'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR',
            'CYCLE', 'DATA', 'DATE', 'DAY', 'DEALLOCATE', 'DEC', 'DECIMAL',
            'DECLARE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE',
            'DEPTH', 'DEREF', 'DESC', 'DESCRIBE', 'DESCRIPTOR', 'DESTROY',
            'DESTRUCTOR', 'DETERMINISTIC', 'DICTIONARY', 'DIAGNOSTICS',
            'DISCONNECT', 'DISTINCT', 'DOMAIN', 'DOUBLE', 'DROP',
            'DYNAMIC', 'EACH', 'ELSE', 'END', 'END_EXEC',
            'EQUALS', 'ESCAPE', 'EVERY', 'EXCEPT', 'EXCEPTION',
            'EXEC', 'EXECUTE', 'EXTERNAL', 'FALSE', 'FETCH',
            'FIRST', 'FLOAT', 'FOR', 'FOREIGN', 'FOUND',
            'FROM', 'FREE', 'FULL', 'FUNCTION', 'GENERAL',
            'GET', 'GLOBAL', 'GO', 'GOTO', 'GRANT',
            'GROUP', 'GROUPING', 'HAVING', 'HOST', 'HOUR',
            'IDENTITY', 'IGNORE', 'IMMEDIATE', 'IN', 'INDICATOR',
            'INITIALIZE', 'INITIALLY', 'INNER', 'INOUT', 'INPUT',
            'INSERT', 'INT', 'INTEGER', 'INTERSECT', 'INTERVAL',
            'INTO', 'IS', 'ISOLATION', 'ITERATE', 'JOIN',
            'LANGUAGE', 'LARGE', 'LAST', 'LATERAL',
            'LEADING', 'LEFT', 'LESS', 'LEVEL', 'LIKE',
            'LIMIT', 'LOCAL', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCATOR',
            'MAP', 'MATCH', 'MINUTE', 'MODIFIES', 'MODIFY',
            'MODULE', 'MONTH', 'NAMES', 'NATIONAL', 'NATURAL',
            'NCHAR', 'NCLOB', 'NEW', 'NEXT', 'NO',
            'NONE', 'NOT', 'NULL', 'NUMERIC', 'OBJECT',
            'OF', 'OFF', 'OLD', 'ON', 'ONLY',
            'OPEN', 'OPERATION', 'OPTION', 'OR', 'ORDER',
            'ORDINALITY', 'OUT', 'OUTER', 'OUTPUT', 'PAD',
            'PARAMETER', 'PARAMETERS', 'PARTIAL', 'POSTFIX',
            'PRECISION', 'PREFIX', 'PREORDER', 'PREPARE', 'PRESERVE',
            'PRIMARY', 'PRIOR', 'PRIVILEGES', 'PROCEDURE', 'PUBLIC',
            'READ', 'READS', 'REAL', 'RECURSIVE', 'REF',
            'REFERENCES', 'REFERENCING', 'RELATIVE', 'RESTRICT', 'RESULT',
            'RETURN', 'RETURNS', 'REVOKE', 'RIGHT',
            'ROLLBACK', 'ROLLUP', 'ROUTINE', 'ROW', 'ROWS',
            'SAVEPOINT', 'SCHEMA', 'SCROLL', 'SCOPE', 'SEARCH',
            'SECOND', 'SECTION', 'SELECT', 'SEQUENCE',
            'SESSION_USER', 'SET', 'SETS', 'SIZE', 'SMALLINT',
            'SOME', 'SPACE', 'SPECIFIC', 'SPECIFICTYPE', 'SQL',
            'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNING', 'START', 
            'STATEMENT', 'STATIC', 'STRUCTURE', 'SYSTEM_USER', 'TABLE',
            'TEMPORARY', 'TERMINATE', 'THAN', 'THEN', 'TIME',
            'TIMESTAMP', 'TIMEZONE_HOUR', 'TIMEZONE_MINUTE', 'TO', 'TRAILING',
            'TRANSACTION', 'TRANSLATION', 'TREAT', 'TRIGGER', 'TRUE',
            'UNDER', 'UNION', 'UNIQUE', 'UNKNOWN', 'UNNEST',
            'UPDATE', 'USAGE', 'USER', 'USING', 'VALUE',
            'VALUES', 'VARCHAR', 'VARIABLE', 'VARYING', 'VIEW',
            'WHEN', 'WHENEVER', 'WHERE', 'WITH', 'WITHOUT',
            'WORK', 'WRITE', 'YEAR', 'ZONE',
        ],
        'postgres': [
        ],
        'mysql': [
            'KEY',
        ],
        'default': [
            'ACTION', 'KEY', 'PATH', 'ROLE', 'SESSION', 'STATE',
        ],
    }

    def getReservedNames(self):
        if self.reservedNames == None:
            self.reservedNames = self.sqlKeywords['common']
            dbType = self.dictionary[DB_TYPE]
            if dbType in self.sqlKeywords:
                self.reservedNames += self.sqlKeywords[dbType]
            else:
                self.reservedNames += self.sqlKeywords['default']
        return self.reservedNames

    getReservedNames = classmethod(getReservedNames)


class MetaBase(object):
    "Data mapper meta supertype."

    logger     = RequiredFeature('Logger')
    registry   = RequiredFeature('DomainRegistry')
    dictionary = RequiredFeature('SystemDictionary')
    reservedNames = ReservedNames()
    
    def makeSafeTableName(self, naiveName):
        naiveName = self.makeSafeDbName(naiveName)
        style = self.getSQLStyle()
        return style.pythonClassToDBTable(naiveName)
    
    def makeSafeFieldName(self, naiveName):
        naiveName = self.makeSafeDbName(naiveName)
        style = self.getSQLStyle()
        return style.pythonAttrToDBColumn(naiveName)

    def makeSafeDbName(self, naiveName):
        if naiveName.upper() in self.getReservedNames():
            naiveName = 'x' + naiveName
            return self.makeSafeDbName(naiveName)
        else:
            return naiveName

    def getReservedNames(self):
        return self.reservedNames.getReservedNames()

    def getSQLStyle(self):
        if hasattr(SQLObject, 'sqlmeta'):  # SQLObject 0.7
            return SQLObject.sqlmeta.style
        elif hasattr(SQLObject, '_style'): # SQLObject 0.6
            return SQLObject._style
        else:
            raise "Can't find SQLObject style object."
            

class MetaMapper(MetaBase):
    "Describes a Mapper with MetaMapperAttributes."

    def __init__(self, metaDomainObject):
        self.dom = metaDomainObject
        self.isUnique = self.dom.isUnique
        self.isCached = self.dom.isCached
        self.domName = self.dom.name
        self.dbName =  self.makeSafeTableName(self.dom.dbName or self.dom.name)
        self.attributesByName = {}
        self.attributes = []
        for domAttr in self.dom.attributes:
            if not domAttr.isList():
                self.addAttribute(domAttr)

    def addAttribute(self, metaDomainAttribute):
        metaAttribute = MetaMapperAttribute(metaDomainAttribute)
        self.attributes.append(metaAttribute)
        self.attributesByName[metaAttribute.domName] = metaAttribute
        return metaAttribute

    def createMapperClass(self, baseClass):
        mapperAttributes = self.getSQLObjectAttributes()
        mapperAttributes['meta'] = self
        mapperAttributes['map'] = {}
        mapperAttributes['map']['isUnique'] = self.isUnique
        mapperAttributes['map']['isCached'] = self.isCached
        mapperAttributes['_connection'] = DatabaseFacade().getConnection()
        # Set mapper class name from domName, and table attribute from dbName.
        mapper = self.createClass(self.domName, baseClass, mapperAttributes)
        if 'sqlmeta' in sqlobject.main.__dict__:      # table for SQLObject 0.7
            if self.dbName:
                mapper.sqlmeta.table = self.dbName
                if self.isCached:
                    mapper.sqlmeta.cacheValues = True
        return mapper

    def getSQLObjectAttributes(self):
        mapperAttributes = {}
        if not 'sqlmeta' in sqlobject.main.__dict__:  # table for SQLObject 0.6
            if self.dbName:
                mapperAttributes['_table'] = self.dbName
        for a in self.attributes:
            mapperAttributes[a.dbName] = a.createMapperClassAttribute()
        return mapperAttributes

    def createClass(self, name, base, attrs):
        return type(name, (base,), attrs)


class MetaMapperAttribute(MetaBase):
    "Governs the attributes of a Mapper."

    class UndefinedDefault(object):
        pass

    def __init__(self, metaDomainAttribute):
        self.dom = metaDomainAttribute
        self.domName  = self.dom.name
        self.typeName = self.dom.typeName
        self.dbName = self.makeSafeFieldName(self.dom.dbName or self.dom.name)
        if self.dom.isValueRef and hasattr(self.dom, 'default'): 
            self.default = self.dom.default
        elif self.dom.isDomainObjectRef:
            if hasattr(self.dom, 'default') and not self.dom.default:
                self.default = None
            elif not self.dom.isRequired:
                self.default = None
        self.isDomainObjectRef = self.dom.isDomainObjectRef

    def createMapperClassAttribute(self):
        "Creates SQLObject columns for new SQLObject classes."
        if issubclass(self.dom.__class__, dm.dom.meta.String):
            if hasattr(self, 'default'):
                return StringCol(default=self.default)
            else:
                return StringCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.DateTime):
            if hasattr(self, 'default'):
                return DateTimeCol(default=self.default)
            else:
                return DateTimeCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Boolean):
            if hasattr(self, 'default'):
                return BoolCol(default=self.default)
            else:
                return BoolCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Integer):
            if hasattr(self, 'default'):
                return IntCol(default=self.default)
            else:
                return IntCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.DomainObjectRef):
            if hasattr(self, 'default'):
                return ForeignKey(self.typeName, default=self.default)
            else:
                return ForeignKey(self.typeName)
        else:
            raise "Unknown domain attribute: %s" % self.dom

    def createNamedMapperClassAttribute(self):
        "Creates SQLObject columns for existing SQLObject classes."
        if issubclass(self.dom.__class__, dm.dom.meta.String):
            if hasattr(self, 'default'):
                return StringCol(name=self.dbName, default=self.default)
            else:
                return StringCol(name=self.dbName)
        elif issubclass(self.dom.__class__, dm.dom.meta.DateTime):
            if hasattr(self, 'default'):
                return DateTimeCol(default=self.default)
            else:
                return DateTimeCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Boolean):
            if hasattr(self, 'default'):
                return BoolCol(default=self.default)
            else:
                return BoolCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.Integer):
            if hasattr(self, 'default'):
                return IntCol(default=self.default)
            else:
                return IntCol()
        elif issubclass(self.dom.__class__, dm.dom.meta.DomainObjectRef):
            if hasattr(self, 'default'):
                return KeyCol(foreignKey=self.typeName, name=self.dbName+'ID',
                    default=self.default
                )
            else:
                return KeyCol(foreignKey=self.typeName, name=self.dbName+'ID')
        else:
            raise "Unknown domain attribute: %s" % self.dom


class Mapper(SQLObject):
    "Maps values between DomainObject and a database."

    class sqlmeta:
        cacheValues = True
        lazyUpdate = True 

    domainObject = None

    def __init__(self, **kwds):
        self.coerceKwds(kwds)
        super(Mapper, self).__init__(**kwds)

    def isUnique(self):
        if 'isUnique' in self.map: 
            return self.map['isUnique']
        else:
            return False

    isUnique = classmethod(isUnique)
    
    def isCached(self):
        if 'isCached' in self.map: 
            isCached = self.map['isCached']
        else:
            isCached = False
        return isCached

    isCached = classmethod(isCached)
    
    def assertCreateParams(self, *args, **kwds):
        if self.isUnique():
            self.assertUnique(*args, **kwds)
        
    assertCreateParams = classmethod(assertCreateParams)
    
    def assertUnique(self, *args, **kwds):
        "Raises exception unless no record exists with given parameters."
        records = self.selectByKeywords(**kwds)
        if kwds and records.count():
            msg = "'%s' record already exists for: %s" % (self.__name__, kwds)
            raise KforgeDbError, msg

    assertUnique = classmethod(assertUnique)
    
    def getDomainObject(self, loadedList=None):
        "Method to 'Lazy Load' mapped domain object."
        if loadedList == None:
            loadedList = dict()
        if not self.domainObject:
            obj = self.createDomainObject() 
            self.domainObject = obj 
            self.domainObject.record = self
            if debug:
                message = "Record returned newly instantiated %s." % self.getClassName()
                logger.debug(message)
            self.loadDomainObject(loadedList, sync=False)
        else:
            if not self.isCached():
                if not self.domainObject in loadedList:
                    if debug:
                        message = "Record loads existing %s instance with values." % self.getClassName()
                        logger.debug(message)
                    self.loadDomainObject(loadedList)
                else:
                    if debug:
                        message = "Loaded %s record avoids loading loop." % self.getClassName()
                        logger.debug(message)
            else: 
                if debug:
                    message = "Record returned %s with existing values." % self.getClassName()
                    logger.debug(message)
        return self.domainObject

    def createDomainObject(self):
        "Creates recorded domain object."
        domainClass = self.getDomainClass()
        if debug:
            message = "Instantiating domain object from: %s" % domainClass
            logger.debug(message)
        domainObject = domainClass()
        return domainObject
       
    def getClassName(self):
        return self.__class__.__name__
        
    def getDomainClass(self):
        "Returns mapper's synonymous domain model class." 
        className = self.getClassName()
        registry = RequiredFeature('DomainRegistry')
        return registry.getDomainClass(className)

    def loadDomainObject(self, loadedList, sync=True):
        "Maps values from record to domain object."
        if sync:
            if debug:
                message = "Synchronising mapper values with RDBMS."
                logger.debug(message)
            self.sync()
        elif sync:
            if debug:
                message = "Not synchronising mapper values with RDBMS."
                logger.debug(message)
        if debug:
            message = "Loading domain object values from mapper."
            logger.debug(message)
        self.domainObject.id = self.id
        for metaAttr in self.meta.attributes:
            dbName = metaAttr.dbName
            domName = metaAttr.domName
            if metaAttr.isDomainObjectRef:
                mapper = getattr(self, dbName)
                if mapper:
                    mappedValue = mapper.getDomainObject(loadedList)
                else:
                    mappedValue = None
                setattr(self.domainObject, domName, mappedValue)
            else:
                mappedValue = getattr(self, dbName)
                setattr(self.domainObject, domName, mappedValue)
        loadedList[self.domainObject] = self.domainObject

    def saveDomainObject(self):
        "Sets attributes of record object from domain object."
        isChanged = False
        for metaAttr in self.meta.attributes:
            if metaAttr.isDomainObjectRef:
                domainObject = getattr(self.domainObject, metaAttr.domName)
                if domainObject and hasattr(domainObject, 'record'):
                    domRecord = domainObject.record
                else:
                    domRecord = None
                dbRecord = getattr(self, metaAttr.dbName)
                if domRecord != dbRecord:
                    setattr(self, metaAttr.dbName, domRecord)
                    isChanged = True
            else:
                domValue = getattr(self.domainObject, metaAttr.domName)
                dbValue = getattr(self, metaAttr.dbName)
                if domValue != dbValue:
                    setattr(self, metaAttr.dbName, domValue)
                    isChanged = True
        if isChanged:
            if debug:
                message = "Updating RDBMS with %s mapper value." % (
                    self.meta.domName
                )
                logger.debug(message)
            self.syncUpdate()

    def coerceKwds(self, kwds):
        "Translates incoming keyword parameters."
        for metaAttr in self.meta.attributes:
            if metaAttr.domName in kwds:
                if metaAttr.isDomainObjectRef:
                    mapper = kwds[metaAttr.domName]
                    del kwds[metaAttr.domName]
                    if mapper:
                        kwds[metaAttr.dbName +'ID'] = mapper.id
                    else:
                        kwds[metaAttr.dbName +'ID'] = None
                else:
                    value = kwds[metaAttr.domName]
                    del kwds[metaAttr.domName]
                    kwds[metaAttr.dbName] = value

    coerceKwds = classmethod(coerceKwds)

    def startsWith(self, value, attributeName, **kwds):
        dbName = self.getAttributeDbName(attributeName)
        sqlSafeName = self.makeSqlName(dbName)
        sqlLike = "UPPER(%s) LIKE UPPER('%s')" % (sqlSafeName, value+'%')
        sqlWhere = " ( " + sqlLike + " ) "
        self.coerceKwds(kwds)
        for name in kwds:
            value = kwds[name]
            # todo: expand for all database systems
            sqlSafeValue = sqlrepr(value, 'postgres')
            sqlSafeName = self.makeSqlName(name)
            sqlEquals = "%s = %s" % (sqlSafeName, sqlSafeValue)
            sqlWhere += " AND ( " + sqlEquals + " ) "
        try:
            sqlWhere = "(" + sqlWhere + ")"
            selection = self.select(sqlWhere)
        except Exception, inst:
            msg = "Couldn't execute select() with %s: %s" % (sqlWhere, inst)
            raise KforgeDbError, msg
        return selection
        
    startsWith = classmethod(startsWith)

    def getAttributeDbName(self, domName):
        metaAttribute = self.meta.attributesByName[domName]
        return metaAttribute.dbName

    getAttributeDbName = classmethod(getAttributeDbName)

    def makeSqlName(self, name):
        #return self.q.__getattr__(name)
        if name[-2:] == 'ID':
            name = name[:-2] + '_id'
        return name

    makeSqlName = classmethod(makeSqlName)
    
    def search(self, userQuery, attributeNames, **kwds):
        dbNames = []
        for attributeName in attributeNames:
            dbName = self.getAttributeDbName(attributeName)
            dbNames.append(dbName)
        sqlLikeList = []
        # todo: expand for all database systems
        sqlSafeQuery = sqlrepr(userQuery, 'postgres')[1:-1] # drop quotes
        for term in sqlSafeQuery.split(' '):
            if term:
                for name in dbNames:
                    sqlSafeName = self.makeSqlName(name)
                    sqlLike = "UPPER(%s) LIKE UPPER('%s')" % (
                        sqlSafeName,'%'+term+'%'
                    )
                    sqlLikeList.append(sqlLike)
            if len(sqlLikeList):
                sqlLike = "(" + ") OR (".join(sqlLikeList) + ")"
            else:
                sqlLike = 'FALSE'
        self.coerceKwds(kwds)
        sqlEqualsList = []
        for name in kwds:
            value = kwds[name]
            # todo: expand for all database systems
            sqlSafeValue = sqlrepr(value, 'postgres')
            sqlSafeName = self.makeSqlName(name)
            sqlEquals = "%s = %s" % (sqlSafeName, sqlSafeValue)
            sqlEqualsList.append(sqlEquals)
        sqlEquals = "(" + ") AND (".join(sqlEqualsList) + ")"
        sqlWhere = '((%s) AND (%s))' % (sqlLike, sqlEquals)
        try:
            selection = self.select(sqlWhere)
        except Exception, inst:
            msg = "Couldn't execute select() with %s: %s" % (sqlWhere, inst)
            raise KforgeDbError, msg
        return selection
       
    search = classmethod(search)

    def selectByKeywordsWithId(self, **kwds):
        self.coerceKwds(kwds)
        sqlEqualsList = []
        for name in kwds:
            value = kwds[name]
            # todo: expand for all database systems
            sqlSafeValue = sqlrepr(value, 'postgres')
            sqlSafeName = self.makeSqlName(name)
            sqlEquals = "%s = %s" % (sqlSafeName, sqlSafeValue)
            sqlEqualsList.append(sqlEquals)
        sqlEquals = "(%s)" % ") AND (".join(sqlEqualsList)
        sqlWhere = '(%s)' % (sqlEquals)
        try:
            selection = self.select(sqlWhere)
        except Exception, inst:
            msg = "Couldn't execute select() with %s: %s" % (sqlWhere, inst)
            raise KforgeDbError, msg
        return selection

    selectByKeywordsWithId = classmethod(selectByKeywordsWithId)
    
    def selectByKeywordsWithTimeInterval(self, **kwds):
        self.coerceKwds(kwds)
        sqlEqualsList = []
        for name in kwds:
            value = kwds[name]
            # todo: expand for all database systems
            sqlSafeValue = sqlrepr(value, 'postgres')
            if name == '__startsBefore__':
                sqlSafeName = self.makeSqlName('starts')
                sqlEquals = "%s < %s" % (
                    sqlSafeName, sqlSafeValue
                )
                sqlEqualsList.append(sqlEquals)
            elif name == '__startsAfter__':
                sqlSafeName = self.makeSqlName('starts')
                sqlEquals = "%s > %s" % (
                    sqlSafeName, sqlSafeValue
                )
                sqlEqualsList.append(sqlEquals)
            elif name == '__endsBefore__':
                sqlSafeName = self.makeSqlName('ends')
                sqlEquals = "%s < %s" % (
                    sqlSafeName, sqlSafeValue
                )
                sqlEqualsList.append(sqlEquals)
            elif name == '__endsAfter__':
                sqlSafeName = self.makeSqlName('ends')
                sqlEquals = "%s > %s" % (
                    sqlSafeName, sqlSafeValue
                )
                sqlEqualsList.append(sqlEquals)
            else:
                sqlSafeName = self.makeSqlName(name)
                sqlEquals = "%s = %s" % (sqlSafeName, sqlSafeValue)
                sqlEqualsList.append(sqlEquals)
        sqlEquals = "(%s)" % ") AND (".join(sqlEqualsList)
        sqlWhere = '(%s)' % (sqlEquals)
        try:
            selection = self.select(sqlWhere)
        except Exception, inst:
            msg = "Couldn't execute select() with %s: %s" % (sqlWhere, inst)
            raise KforgeDbError, msg
        return selection

    selectByKeywordsWithTimeInterval = classmethod(
        selectByKeywordsWithTimeInterval
    )
    
    def selectByKeywords(self, **kwds):
        "Selects records from database using domain object attribute names."
        self.coerceKwds(kwds)
        try:
            selection = self.selectBy(**kwds)
        except Exception, inst:
            msg = "Couldn't execute selectBy() with %s: %s" % (kwds, inst)
            raise KforgeDbError, msg
        return selection
       
    selectByKeywords = classmethod(selectByKeywords)

