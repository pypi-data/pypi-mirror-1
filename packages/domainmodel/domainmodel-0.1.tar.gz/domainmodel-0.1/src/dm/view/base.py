import md5
from dm.ioc import *
from dm.exceptions import *
from dm.dictionarywords import *
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.view.manipulator import FormWrapper
from django.core import template_loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.datastructures import MultiValueDict
from django.template import Context

class ControlledAccessView(object):

    accessController = RequiredFeature('AccessController')
    dictionary       = RequiredFeature('SystemDictionary')
    commands         = RequiredFeature('CommandSet')
    logger           = RequiredFeature('Logger')
    registry         = RequiredFeature('DomainRegistry')
    debug            = RequiredFeature('Debug')  # deprecated
    isDebug          = RequiredFeature('Debug')  # rename for debug

    AUTH_SESSION_COOKIE_NAME = dictionary['auth_cookie_name']
    NO_AUTH_SESSION_COOKIE_STRING = dictionary['no_auth_cookie_name']
    if 'auth_cookie_domain' in dictionary:
        AUTH_COOKIE_DOMAIN = dictionary['auth_cookie_domain']
    else:
        # prefix with '.' to match subdomains
        AUTH_COOKIE_DOMAIN = '.' + dictionary['domain_name']

    def __init__(self, request=None, **kwds):
        self.request = request
        self.response = None
        self.session = None
        # todo: clarify meaning of redirect and redirectPath
        self.redirect = ''
        self.redirectPath = ''
        self.returnPath = ''
        # todo: clean up all this guff
        self._canReadSystem = None
        self._canUpdateSystem = None
        self._canCreatePerson = None
        self._canReadPerson = None
        self._canUpdatePerson = None
        self._canDeletePerson = None
        self._canCreateProject = None
        self._canReadProject = None
        self._canUpdateProject = None
        self._canDeleteProject = None
        self._canCreateMember = None
        self._canReadMember = None
        self._canUpdateMember = None
        self._canDeleteMember = None
        self._canCreateService = None
        self._canReadService = None
        self._canUpdateService = None
        self._canDeleteService = None

    def getMethodName(self):
        if self.request.POST:
            return 'POST'
        else:
            return 'GET'
        
    def setSessionFromCookieString(self, cookieString):
        try:
            sessionKey = self.makeSessionKeyFromCookieString(cookieString)
        except KforgeSessionCookieValueError:
            self.session = None
            if self.debug:
                self.logger.debug(
                    'Session cookie value error: %s' % cookieString
                )
        else:
            self.session = self.findSession(sessionKey)
            if self.session:
                self.session.updateLastVisited()
                if self.debug:
                    self.logger.debug(
                        'Session re-established: %s' % self.session
                    )
            else:
                if self.debug:
                    self.logger.debug(
                        'No session for sessionKey: %s' % sessionKey
                    )

    def makeSessionKeyFromCookieString(self, cookieString):
        sessionKey = cookieString[:32]
        checkString = cookieString[32:]
        if checkString == self.makeCheckString(sessionKey):
            return sessionKey
        else:
            raise KforgeSessionCookieValueError(cookieString)

    def makeCookieStringFromSessionKey(self, sessionKey):
        return sessionKey + self.makeCheckString(sessionKey) 

    def makeCheckString(self, sessionKey):
        secretKey = self.dictionary['django.secret_key']
        return md5.new(sessionKey + secretKey + 'auth').hexdigest()

    def findSession(self, sessionKey):
        if not sessionKey:
            return None
        if sessionKey in self.registry.sessions:
            return self.registry.sessions[sessionKey]
        else:
            return None

    def checkAccessControl(self):
        if self.canAccess():
            return True
        else:
            self.setRedirectAccessDenied()
            return False

    def canAccess(self):
        return False

    def authoriseActionObject(self, actionName, protectedObject):
        if self.session:
            person = self.session.person
        else:
            person = None
        return self.isAuthorised(
            person=person,
            actionName=actionName, 
            protectedObject=protectedObject
        )

    def isAuthorised(self, *args, **kwds):
        return self.accessController.isAuthorised(*args, **kwds)
    
    def canCreate(self, protectedObject):
        return self.authoriseActionObject('Create', protectedObject)

    def canRead(self, protectedObject):
        return self.authoriseActionObject('Read', protectedObject)

    def canUpdate(self, protectedObject):
        return self.authoriseActionObject('Update', protectedObject)

    def canDelete(self, protectedObject):
        return self.authoriseActionObject('Delete', protectedObject)

    def getDomainClass(self, domainClassName):
        return self.registry.getDomainClass(domainClassName)

    def canReadSystem(self):
        if self._canReadSystem == None:
            protectedObject = self.getDomainClass('System')
            self._canReadSystem = self.canRead(protectedObject)
        return self._canReadSystem

    def canUpdateSystem(self):
        if self._canUpdateSystem == None:
            protectedObject = self.getDomainClass('System')
            self._canUpdateSystem = self.canUpdate(protectedObject)
        return self._canUpdateSystem

    def canCreatePerson(self):
        if self._canCreatePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canCreatePerson = self.canCreate(protectedObject)
        return self._canCreatePerson

    def canReadPerson(self):
        if self._canReadPerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canReadPerson = self.canRead(protectedObject)
        return self._canReadPerson

    def canUpdatePerson(self):
        if self._canUpdatePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canUpdatePerson = self.canUpdate(protectedObject)
        return self._canUpdatePerson

    def canDeletePerson(self):
        if self._canDeletePerson == None:
            if self.person:
                protectedObject = self.person
            else:
                protectedObject = self.getDomainClass('Person')
            self._canDeletePerson = self.canDelete(protectedObject)
        return self._canDeletePerson

    def canCreateProject(self):
        if self._canCreateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canCreateProject = self.canCreate(protectedObject)
        return self._canCreateProject

    def canReadProject(self):
        if self._canReadProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canReadProject = self.canRead(protectedObject)
        return self._canReadProject

    def canUpdateProject(self):
        if self._canUpdateProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canUpdateProject = self.canUpdate(protectedObject)
        return self._canUpdateProject

    def canDeleteProject(self):
        if self._canDeleteProject == None:
            if self.project:
                protectedObject = self.project
            else:
                protectedObject = self.getDomainClass('Project')
            self._canDeleteProject = self.canDelete(protectedObject)
        return self._canDeleteProject

    def canCreateMember(self):
        if self._canCreateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canCreateMember = self.canCreate(protectedObject)
        return self._canCreateMember

    def canReadMember(self):
        if self._canReadMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canReadMember = self.canRead(protectedObject)
        return self._canReadMember

    def canUpdateMember(self):
        if self._canUpdateMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canUpdateMember = self.canUpdate(protectedObject)
        return self._canUpdateMember

    def canDeleteMember(self):
        if self._canDeleteMember == None:
            if self.member:
                protectedObject = self.member
            else:
                protectedObject = self.getDomainClass('Member')
            self._canDeleteMember = self.canDelete(protectedObject)
        return self._canDeleteMember

    def canCreateService(self):
        if self._canCreateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canCreateService = self.canCreate(protectedObject)
        return self._canCreateService

    def canReadService(self):
        if self._canReadService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canReadService = self.canRead(protectedObject)
        return self._canReadService

    def canUpdateService(self):
        if self._canUpdateService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canUpdateService = self.canUpdate(protectedObject)
        return self._canUpdateService

    def canDeleteService(self):
        if self._canDeleteService == None:
            if self.service:
                protectedObject = self.service
            else:
                protectedObject = self.getDomainClass('Service')
            self._canDeleteService = self.canDelete(protectedObject)
        return self._canDeleteService

    def getResponse(self):
        return HttpResponse('Sorry, the getResponse() method is not implemented on class %s' % self.__class__)


class SessionView(ControlledAccessView):

    #templateLoader = TemplateLoader()
    templatePath = None
    majorNavigation = []
    majorNavigationItem = "/"
    minorNavigation = []
    minorNavigationItem = "/"

    def __init__(self, **kwds):
        super(SessionView, self).__init__(**kwds)
        self.template     = None
        self.context      = None
        self.sessionCookieString = ''
        self.person = None
        self.project = None
        self.member = None
        self.service = None
        self.readRequest()
        self.rememberme = None

    def __repr__(self):
        return "<%s redirect='%s' redirectPath='%s'>" % (
            self.__class__.__name__, self.redirect, self.redirectPath
        )

    def readRequest(self):
        if not self.request:
            if self.debug:
                self.logger.debug('No request object in view.')
            return
        self.setPathFromRequest()
        self.readRequestSession()
        self.logger.info('Request to %s: %s' % (
            self.__class__.__name__, self.path
        ))

    def setPathFromRequest(self):
        uriPrefix = self.dictionary[URI_PREFIX]
        requestPath = self.request.path 
        if uriPrefix and requestPath.startswith(uriPrefix):
            self.path = requestPath.replace(uriPrefix, '', 1)
        else:
            self.path = requestPath

    def readRequestSession(self):
        "Determines session from a cookie in request."
        cookieName = self.AUTH_SESSION_COOKIE_NAME
        cookieString = self.request.COOKIES.get(cookieName, '')
        if not cookieString:
            if self.debug:
                self.logger.debug('No KForge session cookie in request.')
            return
        if cookieString == self.NO_AUTH_SESSION_COOKIE_STRING:
            if self.debug:
                self.logger.debug('Unauthenticated session cookie in request.')
            return
        if self.debug:
            self.logger.debug('Session cookie in request...')
        self.setSessionFromCookieString(cookieString)
        if self.session:
            self.session.updateLastVisited()
            if self.debug:
                self.logger.debug('Session re-established: %s' % self.session)
        else:
            if self.debug:
                self.logger.debug('No session for cookieString: %s' % cookieString)
        
    def getResponse(self):
        if self.checkAccessControl():
            self.logViewResponse(self.getMethodName(), 'OK')
            self.takeAction()
        else:
            self.logViewResponse(self.getMethodName(), 'DENIED')
        if not self.redirect:
            self.createContext()
        if not self.redirect:
            self.markNavigation()
        if not self.redirect:
            self.setContext()
        self.createResponse()
        self.setSessionCookie()
        return self.response

    def logViewResponse(self, methodName, accessDecisionName):
        if self.session:
            userName = self.session.person.name
        else:
            userName = 'visitor'
        self.logger.info(
            "%s %s %s %s %s" % (
                accessDecisionName,
                userName,
                methodName,
                self.__class__.__name__,
                self.path,
            )
        )

    def takeAction(self):
        pass

    def createContext(self):
        self.context = Context()
    
    def markNavigation(self):
        self.markMajorNavigation()
        self.markMinorNavigation()

    def markMajorNavigation(self):
        self.setMajorNavigationItem()
        self.setMajorNavigationItems()
        self.markCurrentNavigationItem(
            self.majorNavigation, self.getMajorNavigationItem()
        )
    
    def getMajorNavigationItem(self):
        return self.majorNavigationItem

    def markMinorNavigation(self):
        self.setMinorNavigationItem()
        self.setMinorNavigationItems()
        self.markCurrentNavigationItem(
            self.minorNavigation, self.getMinorNavigationItem()
        )

    def getMinorNavigationItem(self):
        return self.minorNavigationItem

    def setMajorNavigationItems(self):
        pass
    
    def setMinorNavigationItems(self):
        pass
    
    def setMajorNavigationItem(self):
        pass
    
    def setMinorNavigationItem(self):
        pass
    
    def markCurrentNavigationItem(self, items, value):
        self.setCurrentItem(items, value, 'url')

    def setCurrentItem(self, items, value='', name=''):
        for item in items:
            if name and (item[name] == value):
                item['isCurrentItem'] = True
            else:
                item['isCurrentItem'] = False

    def createResponse(self):
        if self.redirect:
            self.response = HttpResponseRedirect(self.redirect)
        else:
            self.createContent()
            self.response = HttpResponse(self.content)
           
    def createContent(self):
        self.content = self.renderContextWithTemplate()
    
    def renderContextWithTemplate(self):
        template = self.getTemplate()
        context = self.getContext()
        self.logger.debug("Rendering template '%s' for context: %s" % (
            self.templatePath, context
        ))
        return template.render(context)

    def getTemplate(self):
        if self.template == None:
            self.loadTemplate()
        return self.template

    def loadTemplate(self):
        templatePath = self.getTemplatePath()
        templatePath += ".html"
        self.template = template_loader.get_template(templatePath)
 
    def getTemplatePath(self):
        if self.templatePath == None:
            self.templatePath = self.makeTemplatePath()
        if not self.templatePath:
            raise "No templatePath set on %s" % self
        return self.templatePath

    def makeTemplatePath(self):
        raise "No templatePath for view: %s" % self

    def getViewPosition(self):
        return self.getTemplatePath()

    def getContext(self):
        if self.context == None:
            self.createContext()
            self.setContext()
        return self.context

    def setContext(self, **kwds):
        domainName = self.dictionary['domain_name']
        if self.dictionary['www.port_http'] != '80':
            systemServicePort = self.dictionary['www.port_http']
            systemServiceSocket = domainName +":"+ systemServicePort
        else:
            systemServiceSocket = domainName
            
        mediaHost = self.dictionary['www.media_host']
        if self.dictionary['www.media_port'] != '80':
            mediaPort = self.dictionary['www.media_port']
            systemMediaSocket = mediaHost +":"+ mediaPort
        else:
            systemMediaSocket = mediaHost
        
        self.context.update({
            'view'              : self,
            'uriPrefix'         : self.dictionary[URI_PREFIX],
            'mediaPrefix'       : self.dictionary[MEDIA_PREFIX],
            'isDebug'           : self.isDebug,
            'systemVersion'     : self.dictionary[SYSTEM_VERSION],
            'viewClassName'     : self.__class__.__name__,
            'path'              : self.path,
            'session'           : self.session,
            'redirect'          : self.redirectPath,
            'returnPath'        : self.returnPath,
            'systemServiceName' : self.dictionary[SYSTEM_SERVICE_NAME],
            'systemServiceSocket': systemServiceSocket,
            'systemMediaSocket' : systemMediaSocket,
        })
        self.setWiderContext(**kwds)
        self.setMinorNavigationContext()

    def setWiderContext(self, **kwds):
        self.setMajorNavigationContext()

    def setMajorNavigationContext(self):
        self.context.update({
            'majorNavigation': self.majorNavigation,
        })

    def setMinorNavigationContext(self):
        self.context.update({
            'minorNavigation': self.minorNavigation,
        })

    def setRedirect(self, redirectPath):
        redirectPath = self.dictionary[URI_PREFIX] + redirectPath
        self.logger.info('Redirecting to: %s' % redirectPath)
        self.redirect = redirectPath
    
    def setRedirectLogin(self, returnPath=''):
        if not returnPath:
            if self.request:
                returnPath = self.path
        if returnPath:
            self.logger.info('Returning later to: %s' % returnPath)
        self.setRedirect('/login/' + returnPath)
    
    def setRedirectAccessDenied(self):
        if self.session:
            deniedPath = self.path
            self.setRedirect('/accessDenied/' + deniedPath)
        else:
            self.setRedirectLogin()
    
    def setSessionCookie(self):
        "Sets a cookie identifying the session in the response."
        cookieString = ''
        if self.session:
            cookieString = self.makeCookieStringFromSessionKey(self.session.key)
        else:
            cookieString = self.NO_AUTH_SESSION_COOKIE_STRING
        cookieName = self.AUTH_SESSION_COOKIE_NAME
        cookieDomain = self.AUTH_COOKIE_DOMAIN
        if self.rememberme:
            maxAge = 315360000
        else:
            maxAge = None
        self.response.set_cookie(
            cookieName, cookieString, domain=cookieDomain, max_age=maxAge
        )

    def startSession(self, person):
        self.session = person.sessions.create()
        self.person = person
        self.logger.info("Started session: %s" % self.session)
        
    def stopSession(self):
        if self.session:
            self.logger.info("Stopping session: %s" % self.session)
            self.session.delete()
            self.session = None
        else:
            self.logger.info("Stopping session, but there was no session.")


class AbstractClassView(SessionView):

    registerSizeThreshold = 50

    def __init__(self, domainClassName=None, **kwds):
        super(AbstractClassView, self).__init__(**kwds)
        if domainClassName:
            self.domainClassName = domainClassName
        self.domainObject = None
        self.domainObjectKey = None

    def getDomainObjectRegister(self):
        domainClass = self.getDomainClass(self.domainClassName)
        return domainClass.createRegister()

    def getManipulatedObjectRegister(self):
        return self.getDomainObjectRegister()

    def setContext(self):
        super(AbstractClassView, self).setContext()
        self.context.update({
            'domainClassName' : self.domainClassName,
        })

    def getDomainObject(self):
        if self.domainObject == None:
            if self.domainObjectKey:
                objectRegister = self.getDomainObjectRegister()
                if objectRegister.isStateful:
                    self.domainObject = objectRegister.all[self.domainObjectKey]
                else:
                    self.domainObject = objectRegister[self.domainObjectKey]
        return self.domainObject
        

class AbstractInstanceView(AbstractClassView):

    def __init__(self, domainObjectKey=None, **kwds):
        super(AbstractInstanceView, self).__init__(**kwds)
        self.domainObjectKey = domainObjectKey
        self.manipulator = None

    def setContext(self):
        super(AbstractInstanceView, self).setContext()
        domainObject = self.getDomainObject()
        self.context.update({
            'domainObjectKey' : self.domainObjectKey,
            'domainObject'    : domainObject,
        })

    def getManipulator(self):
        if self.manipulator == None:
            self.manipulator = self.buildManipulator()
        return self.manipulator

    def buildManipulator(self):
        manipulatorClass = self.getManipulatorClass()
        objectRegister   = self.getManipulatedObjectRegister()
        domainObject     = self.getManipulatedDomainObject()
        fieldNames       = self.getManipulatedFieldNames()
        msg = "Building manipulator %s with fields names %s for position %s" % (
            manipulatorClass.__name__,
            fieldNames,
            self.getViewPosition()
        )
        self.logger.debug(msg)
        return manipulatorClass(objectRegister, domainObject, fieldNames)

    def getManipulatedFieldNames(self):
        return []

    def manipulateDomainObject(self):
        pass


class AbstractFormView(AbstractInstanceView):

    def __init__(self, **kwds):
        super(AbstractFormView, self).__init__(**kwds)
        self.form = None
        self.requestParams = None
        self.formErrors = None
        
    def takeAction(self):
        if self.isSubmissionRequest():
            self.manipulateDomainObject()
            if not self.getFormErrors():
                self.setPostManipulateRedirect()
            else:
                self.logger.warning("Form errors on %s: %s" % (
                    self.__class__.__name__, self.formErrors
                ))
        elif not self.getRequestParams():
            self.requestParams = self.getInitialParams()
            self.formErrors = self.getZeroFormErrors() 
                
    def getInitialParams(self):
        return {}

    def isSubmissionRequest(self):
        requestParams = self.getRequestParams()
        countParams = len(requestParams)
        isInitialSubmission = requestParams.has_key('initialise')
        return countParams and not isInitialSubmission

    def getRequestParams(self):
        if self.requestParams == None:
            if self.request.POST:
                self.requestParams = self.request.POST.copy()
            elif self.request.GET:
                self.requestParams = self.request.GET.copy()
            else:
                self.requestParams = self.getZeroRequestParams()
        self.logger.debug("Request params: %s" % self.requestParams)
        return self.requestParams

    def getFormErrors(self):
        if self.formErrors == None:
            if self.getRequestParams():
                self.formErrors = self.getValidationErrors()
            else:
                self.formErrors = self.getZeroFormErrors() 
        self.logger.debug("Form errors: %s" % self.formErrors)
        return self.formErrors

    def getZeroRequestParams(self):
        return {}

    def getZeroFormErrors(self):
        return {}

    def getValidationErrors(self):
        manipulator = self.getManipulator()
        requestParams = self.getRequestParams()
        validationErrors = manipulator.getValidationErrors(requestParams)
        self.logger.debug("Validation errors: %s" % validationErrors)
        return validationErrors
            
    def getForm(self):
        if self.form == None:
            self.form = self.buildForm()
        return self.form

    def getManipulatedDomainObject(self):
        return self.getDomainObject()

    def buildForm(self):
        manipulator = self.getManipulator()
        requestParams = self.getRequestParams()
        if not self.skipFormErrorChecks():
            formErrors = self.getFormErrors()
        else:
            formErrors = self.getZeroFormErrors()
        return FormWrapper(manipulator, requestParams, formErrors)

    def skipFormErrorChecks(self):
        if not self.getRequestParams():
            return False
        elif self.isSubmissionRequest():
            return False
        else:
            return True

    def getManipulatorClass(self):    
        return DomainObjectManipulator

    def setContext(self):
        super(AbstractFormView, self).setContext()
        self.context.update({
            'form'   : self.getForm(),
        })

    def setPostManipulateRedirect(self):
        self.setRedirect(self.makePostManipulateLocation())
        
    def makePostManipulateLocation(self):
        raise "Abstract method not implemented on class %s." % self.__class__.__name__


class AbstractInputFormView(AbstractFormView):

    def manipulateDomainObject(self):
        super(AbstractInputFormView, self).manipulateDomainObject()
        if not self.getFormErrors():
            manipulator = self.getManipulator()
            manipulator.decodeHtml(self.getRequestParams())
        

class AbstractListView(AbstractClassView):

    def setContext(self):
        super(AbstractListView, self).setContext()
        domainClassRegister = self.registry.getDomainClassRegister()
        objectRegister = self.getManipulatedObjectRegister()
        objectRegisterCount = len(objectRegister)
        isRegisterCountLow = objectRegisterCount < self.registerSizeThreshold
        isRegisterCountSingle = objectRegisterCount == 1
        isRegisterCountZero = objectRegisterCount == 0
        self.context.update({
            'domainClassNameList' : domainClassRegister.keys(),  # todo: remove
            'domainObjectList'    : objectRegister,
            'domainClassName'     : objectRegister.typeName,
            'objectRegister'      : objectRegister,
            'registerCount'       : objectRegisterCount,
            'isRegisterCountLow'  : isRegisterCountLow,
            'isRegisterCountSingle' : isRegisterCountSingle,
            'isRegisterCountZero' : isRegisterCountZero,
        })


class AbstractSearchView(AbstractClassView):

    def __init__(self, startsWith='', **kwds):
        super(AbstractSearchView, self).__init__(**kwds)
        self.userQuery = ''
        self.startsWith = startsWith
        if not self.startsWith and self.request.POST:
            self.requestParams = self.request.POST.copy()
            if self.requestParams.has_key('startsWith'):
                self.startsWith = self.requestParams['startsWith']
            else:
                self.userQuery = self.requestParams['userQuery']

    def setContext(self):
        super(AbstractSearchView, self).setContext()
        if self.startsWith or self.userQuery:
            searchResultList = self.searchManipulatedRegister()
            self.context.update({
                'isResultsRequest' : True,
                'domainObjectList' : searchResultList,
                'resultsCount'     : len(searchResultList),
                'isResultSingular' : len(searchResultList) == 1,
                'userQuery'        : self.userQuery.replace('"', '&quot;'),
                'startsWith'       : self.startsWith,
                # todo: Improve above HTML character substitution.
            })

    def searchManipulatedRegister(self):
        if not self.domainClassName:
            raise "No domainClassName on '%s' set." % self
        commandName = self.domainClassName + 'List'
        commandKwds = {}
        commandKwds['userQuery'] = self.userQuery
        commandKwds['startsWith'] = self.startsWith.capitalize()
        if commandName in self.commands:
            commandClass = self.commands[commandName]
        else:
            commandClass = self.commands['DomainObjectList']
            commandKwds['typeName'] = self.domainClassName
        command = commandClass(**commandKwds)
        command.execute()
        return command.results
            

class AbstractCreateView(AbstractInputFormView):

    def getInitialParams(self):
        initialParams = MultiValueDict()
        objectRegister = self.getManipulatedObjectRegister()
        domainClass = self.getDomainClass(objectRegister.typeName)
        for metaAttr in domainClass.meta.attributes:
            if not (hasattr(metaAttr, 'default') and metaAttr.default):
                continue
            if metaAttr.isAssociateList:
                initialParams.setlist(metaAttr.name, metaAttr.default)
            else:
                if callable(metaAttr.default):
                    initialParams[metaAttr.name] = metaAttr.default()
                else:
                    initialParams[metaAttr.name] = metaAttr.default
        return initialParams

    def manipulateDomainObject(self):
        super(AbstractCreateView, self).manipulateDomainObject()
        if not self.getFormErrors():
            manipulator = self.getManipulator()
            manipulator.create(self.getRequestParams())
            if not manipulator.domainObject:
                raise "Create manipulator did not produce an object."
            self.setCreatedObject(manipulator.domainObject)

    def setCreatedObject(self, createdObject):
        self.domainObject = createdObject
    

class AbstractReadView(AbstractInstanceView):

    def setContext(self):
        super(AbstractReadView, self).setContext()
        self.context.update({
            'domainObjectPersonalLabel' : self.getDomainObjectPersonalLabel(),
            'domainObjectNamedValues'  : self.getDomainObjectAsNamedValues(),
        })

    def getDomainObjectAsNamedValues(self):
        domainObject = self.getDomainObject()
        return domainObject.asNamedValues()
        
    def getDomainObjectPersonalLabel(self):
        domainObject = self.getDomainObject()
        if domainObject:
            return domainObject.getPersonalLabel()
        else:
            return ''


class AbstractUpdateView(AbstractInputFormView):

    def getInitialParams(self):
        domainObject = self.getManipulatedDomainObject()
        domainObjectValueDict = domainObject.asDictValues()
        initialParams = MultiValueDict()
        for key in domainObjectValueDict:
            item = domainObjectValueDict[key]
            if hasattr(item, '__class__') and item.__class__.__name__ == 'list':
                initialParams.setlist(key, item)
            else:
                if item == None:
                    initialParams[key] = ''
                else:
                    initialParams[key] = item
        return initialParams
        
    def manipulateDomainObject(self):
        super(AbstractUpdateView, self).manipulateDomainObject()
        if not self.getFormErrors():
            manipulator = self.getManipulator()
            requestParams = self.getRequestParams()
            manipulator.update(data=requestParams)


class AbstractDeleteView(AbstractFormView):

    def __init__(self, **kwds):
        super(AbstractDeleteView, self).__init__(**kwds)
        self.formErrors = {}

    def getInitialParams(self):
        initialParams = MultiValueDict()
        domainObject = self.getManipulatedDomainObject()
        domainObjectValueDict = domainObject.asDictValues()
        initialParams.update(domainObjectValueDict)
        return initialParams

    def manipulateDomainObject(self):
        super(AbstractDeleteView, self).manipulateDomainObject()
        domainObject = self.getManipulatedDomainObject()
        domainObject.delete()


class AbstractHasManyView(AbstractInstanceView):

    def __init__(self, hasManyName=None, hasManyKey=None, **kwds):
        super(AbstractHasManyView, self).__init__(**kwds)
        self.hasManyName = hasManyName
        self.hasManyKey = hasManyKey
        self.hasManyMeta = None
        self.hasManyRegister = None
        self.hasManyValueLabels = None
        self.associationObject = None

    def __repr__(self):
        return "<%s domainClassName='%s' domainObjectKey='%s' hasManyName='%s' hasManyKey='%s' redirect='%s' redirectPath='%s'>" % (self.__class__.__name__, self.domainClassName, self.domainObjectKey, self.hasManyName, self.hasManyKey, self.redirect, self.redirectPath)

    def getManipulatedObjectRegister(self):
        return self.getHasManyRegister()

    def getManipulatedDomainObject(self):
        return self.getAssociationObject()

    def setContext(self):
        super(AbstractHasManyView, self).setContext()
        hasManyClassName = self.getHasManyMeta().typeName
        hasManyRegister = self.getHasManyRegister()
        hasManyValueLabels = self.getHasManyValueLabels()
        associationObject = self.getAssociationObject()
        if associationObject:
            associationObjectNamedValues = associationObject.asNamedValues(
                excludeName=self.getHasManyMeta().owner
            )
        else:
            associationObjectNamedValues = []
        self.context.update({
            'hasManyName'        : self.hasManyName,
            'hasManyClassName'   : hasManyClassName,
            'hasManyRegister'    : hasManyRegister,
            'hasManyKey'         : self.hasManyKey,
            'hasManyValueLabels' : hasManyValueLabels,
            'associationObject'  : associationObject,
            'associationObjectNamedValues' : associationObjectNamedValues,
        })

    def getHasManyMeta(self):
        if not self.hasManyMeta:
            domainObject = self.getDomainObject()
            if not domainObject:
                message = "No domain object when getting meta data: %s" % self
                raise Exception(message)
            if not self.hasManyName in domainObject.meta.attributeNames:
                message = "HasMany name '%s' not in attributes: %s" % (
                    self.hasManyName, domainObject.meta.attributeNames
                )
                raise Exception(message)
            hasManyMeta = domainObject.meta.attributeNames[self.hasManyName]
            self.hasManyMeta = hasManyMeta
        return self.hasManyMeta

    def getHasManyRegister(self):
        if not self.hasManyRegister:
            domainObject = self.getDomainObject()
            self.hasManyRegister = getattr(domainObject, self.hasManyName)
        return self.hasManyRegister

    def getHasManyValueLabels(self):
        if not self.hasManyValueLabels:
            domainObject = self.getDomainObject()
            hasManyMeta = self.getHasManyMeta()
            hasManyValueLabels = hasManyMeta.createValueLabelList(domainObject)
            self.hasManyValueLabels = hasManyValueLabels
        return self.hasManyValueLabels

    def getManipulatorClass(self):    
        return HasManyManipulator

    def getAssociationObject(self):
        if self.associationObject == None:
            if self.hasManyKey:
                domainObject = self.getDomainObject()
                hasManyMeta = self.getHasManyMeta()
                associationObject = hasManyMeta.getAssociationObject(
                    domainObject, self.hasManyKey
                )
                self.associationObject = associationObject
        return self.associationObject


class AbstractListHasManyView(AbstractHasManyView):
    pass

class AbstractCreateHasManyView(AbstractHasManyView, AbstractCreateView):

    def setCreatedObject(self, createdObject):
        self.associationObject = createdObject


class AbstractReadHasManyView(AbstractHasManyView):
    pass

class AbstractUpdateHasManyView(AbstractReadHasManyView, AbstractUpdateView):
    pass

class AbstractDeleteHasManyView(AbstractReadHasManyView, AbstractDeleteView):
    pass

