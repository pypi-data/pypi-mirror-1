import os, shutil

from dm.ioc import *
import dm.exceptions

class PluginController(object):
    "Notifies plugins of core system events. 'Observer (293)' [GoF, 1995]"

    class __singletonPluginController(object):

        registry = RequiredFeature('DomainRegistry')

        def __init__(self):
            self.plugins = None
    
        def notify(self, eventName, eventSender=None):
            "Notifies plugins of domain object events."
            self.checkPlugins()
            if eventName == 'PluginCreate':
                self.onPluginCreate(eventSender)
            if eventName == 'PluginDelete':
                self.onPluginDelete(eventSender)
            for plugin in self.plugins:
                eventReceiverName = 'on' + eventName
                if hasattr(plugin, eventReceiverName):
                    eventHandler = getattr(plugin, eventReceiverName)
                    if callable(eventHandler):
                        eventHandler(eventSender)
        
        def onPluginCreate(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onCreate()
                self.plugins.append(pluginSystem)
        
        def onPluginDelete(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onDelete()
            for pluginSystem in self.plugins:
                if pluginSystem.domainObject == pluginDomainObject:
                    self.plugins.remove(pluginSystem)
        
        def checkPlugins(self):
            "Lazy-loads plugins. Adds and removes plugins from loaded list."
            if self.plugins == None:
                self.plugins = self.getPlugins()

        def getPlugins(self):
            "Returns registered plugin objects."
            pluginSystems = []
            if len(self.registry.plugins.getAll()) == 0:
                return pluginSystems
            for pluginDomainObject in self.registry.plugins:
                pluginSystem = pluginDomainObject.getSystem()
                if not pluginSystem:
                    continue
                pluginSystems.append(pluginSystem)
            return pluginSystems
    
    __instance = __singletonPluginController()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

