from dm.ioc import *
import dm.exceptions
from dm.plugin.base import PluginBase

class PluginFactory(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger     = RequiredFeature('Logger')

    def getPlugin(self, domainObject):
        "Builds plugin system from plugin domain object."
        pluginName = domainObject.name
        pluginClass = self.getPluginClass(pluginName)
        if pluginClass:
            return pluginClass(domainObject)
        else:
            return None

    def getPluginClass(self, pluginName):
        pluginPackage = self.getPluginPackage(pluginName)
        if pluginPackage:
            pluginPackageDict = pluginPackage.__dict__
            for packageAttr in pluginPackageDict.values():
                if not hasattr(packageAttr, '__class__'):
                    continue
                if not packageAttr.__class__ == type:
                    continue
                if not issubclass(packageAttr, PluginBase):
                    continue
                return packageAttr
            msg = "Couldn't find a plugin class for '%s' plugin." % pluginName
            raise dm.exceptions.KforgeMissingPluginSystemClass(msg) 

    def getPluginPackage(self, pluginName):
        "Imports named plugin package."
        pluginPackageName = self.dictionary['plugin_package']
        pluginPackageName += '.' + pluginName
        try:
            pluginPackage = __import__(pluginPackageName, '', '', '*')
            if not pluginPackage:
                raise Exception("No plugin package was imported.")
        except Exception, inst:
            msg = "There was an error importing plugin package '%s': %s." % (
                pluginPackageName, inst
            )
            self.logger.error(msg)
            pluginPackage = None
        return pluginPackage

