import dm
from dm.config import ConfigFileReader
import os
from dm.dictionarywords import *
from dm.environment import SystemEnvironment

class SystemDictionary(dict):
    "Dictionary of system attributes."

    def __init__(self):
        super(SystemDictionary, self).__init__()
        self.assertSystemName()
        self.environment = SystemEnvironment(self.getSystemName())
        self.assertSystemEnvironment()
        self.setDefaultWords()
        self.makeConfigFilePath()
        self.assertConfigFileExists()
        self.makeConfigFileReader()
        self.initConfigFileReader()
        self.readConfigFile()
        self.setConfigWordsFromFile()

    def assertSystemName(self):
        if not self.getSystemName():
            raise "No system name!"
        
    def assertSystemEnvironment(self):
        self.environment.assertDjangoSettingsModule()
        
    def setDefaultWords(self):
        self[PYTHONPATH]          = os.environ.get('PYTHONPATH', '')
        self[SYSTEM_NAME]         = self.getSystemName()
        self[SYSTEM_SERVICE_NAME] = self[SYSTEM_NAME]
        self[SYSTEM_MODE]         = 'production'
        self[SYSTEM_VERSION]      = self.getSystemVersion()
        self[VISITOR_NAME]        = 'visitor'
        self[VISITOR_ROLE]        = 'Visitor'
        self[INITIAL_PERSON_ROLE] = 'Visitor'
        self[PLUGIN_PACKAGE_NAME] = 'dm.plugin'
        self[CAPTCHA_IS_ENABLED]  = '' # False (ConfigParser only supports str)
        self[AUTH_COOKIE_NAME]    = '%s_auth' % self[SYSTEM_NAME]
        self[NO_AUTH_COOKIE_NAME] = '%s_no_auth' % self[SYSTEM_NAME]
        self[LOG_LEVEL]           = 'INFO'
        self[URI_PREFIX]          = ''
        self[MEDIA_PREFIX]        = ''

    def makeConfigFilePath(self):
        self.configFilePath = self.environment.getConfigFilePath()

    def assertConfigFileExists(self):
        if not os.path.exists(self.configFilePath):
            raise "Missing config file: %s" % self.configFilePath

    def makeConfigFileReader(self):
        self.configFileReader = ConfigFileReader()
        
    def initConfigFileReader(self):
        for key in self.keys():
            self.configFileReader[key] = self[key]
        
    def readConfigFile(self):
        pathList = [self.configFilePath]
        self.configFileReader.read(pathList)
        
    def setConfigWordsFromFile(self):
        for configWord in self.configFileReader.keys():
            self[configWord] = self.configFileReader[configWord]
    
    def getSystemVersion(self):
        return dm.__version__

    def getSystemName(self):
        return 'domainmodel'

