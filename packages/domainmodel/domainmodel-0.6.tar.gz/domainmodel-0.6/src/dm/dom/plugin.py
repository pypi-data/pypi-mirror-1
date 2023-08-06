from dm.dom.stateful import *
from dm.ioc import *

def getProjects():
    domainRegistry = RequiredFeature('DomainRegistry')
    return domainRegistry.projects

class Plugin(StandardObject):
    "Registered plugin."

    systemFactory = RequiredFeature('PluginFactory')
   
    def __init__(self, **kwds):
        super(Plugin, self).__init__(**kwds)
        self.__system = None
    
    def initialise(self, register):
        pluginSystem = self.getSystem()
        if pluginSystem:
            pluginSystem.initialise(register)

    def getMaxServicesPerProject(self):
        pluginSystem = self.getSystem()
        if pluginSystem:
            return pluginSystem.getMaxServicesPerProject()
        else:
            return None

    def extendsDomainModel(self):
        return self.getSystem().extendsDomainModel

    def getExtnRegister(self):
        return self.getSystem().getRegister()

    def getExtnObject(self, service):
        extnRegister = self.getSystem().getRegister()
        if service in extnRegister:
            return extnRegister[service]
        else:
            return None

    def getSystem(self):
        "Returns plugin system modelled by domain object."
        if not self.__system:
            self.__system = self.systemFactory.getPlugin(self)
        return self.__system

