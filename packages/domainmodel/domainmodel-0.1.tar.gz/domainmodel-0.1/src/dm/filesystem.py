import os.path
from dm.ioc import *

class FileSystemPathBuilder(object):

    dictionary = RequiredFeature('SystemDictionary')
    
    def __init__(self):
        self.pluginDataPath = self.dictionary['plugin_data_dir']
    
    def getPluginPath(self, plugin):
        "Returns path of directory containing plugin filesystems."
        return os.path.join(self.pluginDataPath, plugin.name)

