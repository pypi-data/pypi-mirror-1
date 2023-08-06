from dm.ioc import RequiredFeature
from dm.dictionarywords import SYSTEM_NAME, SYSTEM_MODE
from dm.dictionarywords import APACHE_RELOAD_CMD, NO_APACHE_RELOAD
from dm.dictionarywords import APACHE_CONFIG_PATH
from dm.environment import SystemEnvironment
import commands

class ApacheConfigBuilder(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.initEnvironment()
        self.initPythonDebugMode()
        self.initConfigEnvVarName()
        self.initConfigFilePath()

    def initEnvironment(self):
        systemName = self.dictionary[SYSTEM_NAME]
        self.environment = SystemEnvironment(systemName)

    def initPythonDebugMode(self):
        if self.dictionary[SYSTEM_MODE] == 'production':
            self.pythonDebugMode = 'Off'
        else:
            self.pythonDebugMode = 'On'

    def initConfigEnvVarName(self):
        varName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.systemConfigEnvVarName = varName

    def initConfigFilePath(self):
        self.systemConfigFilePath = self.environment.getConfigFilePath()

    def reloadConfig(self):
        """
        Reloads config into Apache.
        """
        # todo: Check the return value of reloadConfig() is necessary.
        if self.dictionary[NO_APACHE_RELOAD]:
            msg = "Not reloading apache, '%s' is set." % NO_APACHE_RELOAD
            self.logger.warning(msg)
        else:
            cmd = self.dictionary[APACHE_RELOAD_CMD]
            try:
                errorStatus, output = commands.getstatusoutput(cmd)
                if errorStatus:
                    msg = "Failed to reload apache using '%s': %s" % (
                        cmd, output)
                    self.logger.error(msg)
                    return False
            except Exception, inst:
                self.logger.error('Exception on reload of apache: %s' % inst)
                return False
        return True

    def buildConfig(self):
        "Deprected method name."
        self.buildConfigFile()

    def buildConfigFile(self):
        """
        Creates config content, and writes to config file.
        """
        configPath = self.dictionary[APACHE_CONFIG_PATH]
        configContent = self.createConfigContent()
        file = open(configPath, 'w')
        file.write(configContent)
        file.close()
        self.logger.info("Written new apache config to path: %s" % configPath)

    def getConfig(self):
        "Deprecated method name."
        return self.createConfig()

    def createConfigContent(self):
        return ""


