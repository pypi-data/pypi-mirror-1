import os.path
from dm.ioc import *
from dm.dictionarywords import PLUGIN_DIR_PATH

class FileSystemPathBuilder(object):

    dictionary = RequiredFeature('SystemDictionary')
    
    def __init__(self):
        self.pluginDataPath = self.dictionary[PLUGIN_DIR_PATH]
    
    def getPluginPath(self, plugin):
        "Returns path of directory containing plugin filesystems."
        return os.path.join(self.pluginDataPath, plugin.name)

