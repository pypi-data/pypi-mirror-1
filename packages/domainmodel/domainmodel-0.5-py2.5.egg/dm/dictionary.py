import dm
from dm.config import ConfigFileReader
import os
from dm.dictionarywords import *
from dm.environment import SystemEnvironment
import dm.times
from dm.exceptions import InvalidSystemDictionary

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
        self.setConfigPathInDict()
        self.initTimezone()
        self.validateDictionaryWords()
        self.assertWebkitEnvironment()

    def assertSystemName(self):
        if not self.getSystemName():
            raise Exception, "No system name!"
        
    def assertSystemEnvironment(self):
        pass

    def assertWebkitEnvironment(self):
        if self[WEBKIT_NAME] == 'django':
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
        self[WWW_PORT]            = '80'
        self[NO_APACHE_RELOAD]    = '1'
        self[APACHE_RELOAD_CMD]   = 'sudo /etc/init.d/apache2 reload'
        self[APACHE_CONFIGTEST_CMD] = 'sudo /etc/init.d/apache2 configtest'
        self[URI_PREFIX]          = ''
        self[MEDIA_ROOT]          = ''
        self[MEDIA_HOST]          = ''
        self[MEDIA_PORT]          = '80'
        self[MEDIA_PREFIX]        = ''
        # For values of the TIMEZONE word, please read the information
        # about the TZ environment variable in this tzset() reference:
        #     http://docs.python.org/lib/module-time.html
        self[TIMEZONE]            = 'Europe/Paris'
        self[SKIP_EMAIL_SENDING]  = ''
        self[IMAGES_DIR_PATH]     = '/tmp/%s-images' % self[SYSTEM_NAME]
        self[DB_MIGRATION_IN_PROGRESS] = ''
        self[DJANGO_SECRET_KEY]   = 'f*(d3d45zetsb3)$&2h5@lua()yc+kfn4w^dmrf_j1i(6jjkq'
        self[EDITOR]              = 'editor'
        self[WEBKIT_NAME]         = 'django'

    def makeConfigFilePath(self):
        self.configFilePath = self.environment.getConfigFilePath()

    def setConfigPathInDict(self):
        self[SYSTEM_CONFIG_PATH] = self.configFilePath

    def assertConfigFileExists(self):
        if not os.path.exists(self.configFilePath):
            raise Exception, "Missing config file: %s" % self.configFilePath

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

    def initTimezone(self):
        if self[TIMEZONE]:
            self.environment.setTimezone(self[TIMEZONE])
            dm.times.resetTimezone()

    def set(self, name, value):
        self[name] = value

    def validateDictionaryWords(self):
        self.validateUriPrefix()
        # todo: More dictionary word validation.

    def validateUriPrefix(self):
        uriPrefix = self[URI_PREFIX]
        if uriPrefix == '':
            return
        if uriPrefix[0] != '/':
            msg = "No leading slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        if uriPrefix[-1] == '/':
            msg = "Trainling slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        


