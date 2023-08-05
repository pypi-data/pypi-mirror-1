import os
import sys
import optparse

import dm.environment
from dm.cli.base import CommandLineUtility
from dm.exceptions import KforgeError

class MethodError(object): pass

class AdministrationUtility(CommandLineUtility):
    "Supports command-line system adminstration."
    
    def __init__(self, systemPath=None):
        CommandLineUtility.__init__(self) # old style class
        self.interactive = 0
        self.prompt = '> '
        self.systemPath = systemPath

    def default(self, line):
        print 'Sorry, not a valid command: %s' % line
        errorStatus = 1
        return errorStatus

    def run_interactive(self):
        "Run an interactive session."
        print 'Welcome to interactive mode.'
        print 'Type "?", "help" or "about" for more information.'
        print ''
        while 1:
            try:
                self.cmdloop()
                break
            except KeyboardInterrupt:
                print ''
                print 'Use "quit" or Ctrl-D (i.e. EOF) to exit.'
                print ''

    def buildApplication(self):
        import dm.soleInstance
        
    def convertLineToArgs(self, line):
        unstrippedArgs = line.strip().split()
        self.args = [arg.strip() for arg in unstrippedArgs]
        return self.args

    def do_migratedump(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inappropriate arguments\n'
            self.help_migratedump(line)
            return 1
        dumpFilePath = self.args[0]
        self.buildApplication()
        from dm.migrate import DomainModelDumper
        dataDumper = DomainModelDumper()
        dataDumper.dumpDataToFile(dumpFilePath)

    def help_migratedump(self, line=None):
        usage = \
'''migratedump filepath

Dump service object model
'''
        print usage

    def do_migratedumpfiles(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inappropriate arguments\n'
            self.help_migratedumpfiles(line)
            return 1
        self.buildApplication()
        self.migrateDumpFiles()

    def migrateDumpFiles(self):
        filesDumpDirPath = self.args[0]
        dumper = self.createFilesDumper()
        dumper.dumpInDir(filesDumpDirPath)

    def createFilesDumper(self):
        from dm.migrate import FilesDumper
        return FilesDumper()

    def help_migratedumpfiles(self, line=None):
        usage = \
'''migratedumpfiles dirpath

Dump service filesystem files
'''
        print usage

    def do_migrateload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inappropriate arguments\n'
            self.help_migrateload(line)
            return 1
        dumpFilePath = self.args[0]
        self.buildApplication()
        from dm.migrate import DomainModelLoader
        dataLoader = DomainModelLoader()
        dataLoader.loadDataFromFile(dumpFilePath)

    def help_migrateload(self, line=None):
        usage = \
'''migrateload filepath

Load migrated service data
'''
        print usage

    def do_data(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) != 1:
            print 'ERROR: Insufficient arguments\n'
            self.help_data(line)
            return 1
        elif args[0] == 'create':
            self.initialiseSystemServiceFilesystem()
            return 0
        else:
            self.help_data()
            return 1

    def initialiseSystemServiceFilesystem(self):
        raise Exception, "Method not implemented."

    def help_data(self, line=None):
        usage = \
'''data <action>
  action = create

Create environment data
'''
        print usage

    def do_backup(self, line):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Insufficient arguments\n'
            self.help_backup(line)
            return 1
        else:
            self.backupSystemService()
            return 0

    def backupSystemService(self):
        raise Exception, "Method not implemented."

    def help_backup(self, line=None):
        usage  = 'backup dest\n'
        usage += '\tdest is the path to which you wish to backup'
        print usage
     
    def do_db(self, line=None):
        """Run db commands
        """
        args = self.convertLineToArgs(line)
        if len(args) != 1:
            print 'ERROR: Insufficient arguments\n'
            self.help_db(line)
            return 1

        actionName = args[0]
        if actionName in ['rebuild', 'delete', 'create', 'init']:
            self.takeDatabaseAction(actionName)
            #try:
            #    self.takeDatabaseAction(actionName)
            #except KforgeError, inst:
            #    print 'Command failed. Details: %s' % inst
            #    return 1
        else:
            print "ERROR: action '%s' is not supported\n" % actionName
            self.help_db(line)
            return 1
       
    def takeDatabaseAction(self, actionName):
        dbUtilClass = self.getDatabaseUtilityClass()
        dbUtil = dbUtilClass()
        actionMethod = getattr(dbUtil, actionName)
        actionMethod()

    def getDatabaseUtilityClass(self):
        from dm.util.db import Database
        return Database
       
    def help_db(self, line=None):
        usage  = \
'''db <action>
  action = create | delete | init | rebuild 

NB: A known issue is that due to a persisted db connection once you
have run init or rebuild you cannot run any of the other commands
again in the same session.'''
        # [[TODO: display docstrings for each function from db class here
        # Database.__dict__[cmd].__doc__
        print usage

    def do_upgrade(self, line=None):
        # TODO use system version to specify upgrade script used
        args = self.convertLineToArgs(line)
        if len(args) != 1:
            self.help_upgrade(line)
            return 1
        elif args[0] == 'data':
            self.upgradeSystemServiceFilesystem()
            return 0
        elif args[0] == 'db':
            self.upgradeSystemServiceDatabase()
            return 0
        else:
            print 'Unknown arguments: %s' % args
            self.help_upgrade()

    def upgradeSystemServiceFilesystem(self):
        raise Exception, "Method not implemented."
        
    def upgradeSystemServiceDatabase(self):
        raise Exception, "Method not implemented."
        
    def help_upgrade(self, line=None):
        usage = \
'''upgrade <object>
  object = data | db

Upgrade a KForge service (data and db)'''
        print usage
    
    def do_www(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) == 0:
            self.help_www(line)
            return 1
        self.buildApplication()
        if args[0] == 'build':
            self.buildApacheConfig()
        elif args[0] == 'reload':
            self.reloadApacheConfig()
        else:
            self.help_www(line)
            return 1

    def buildApacheConfig(self):
        raise Exception, "Method not implemented."
        
    def reloadApacheConfig(self):
        raise Exception, "Method not implemented."
      
    def help_www(self, line=None):
        help = 'www [ build | reload ]\n'
        help += '\tbuild: build web server configuration\n'
        help += '\treload: reload web server configuration\n'
        print help

    def do_shell(self, line=None):
        import code
        code.interact()

    def help_shell(self, line=None):
        help = \
'''shell: run a Python interactive shell

Used to administer domain objects. Read docs/cli_shell.txt for a full
guide to use of the shell for administration of the domain model.

Preferred to direct invocation of a python shell as this ensures all relevant
environment variables are correctly set.
'''
        print help

    def do_about(self, args=None):
        print self.createAboutMessage()

    def createAboutMessage(self):
        raise Exception, "Method not implemented."

    def help_about(self, line=None):
        help = \
'''about: print basic information about this application

'''
        print help


    def do_help(self, line=None):
        CommandLineUtility.do_help(self, line)
        
    def help_help(self, line=None):
        help = \
'''help: print information about commands

'''
        print help

    def do_quit(self, line=None):
        sys.exit()
    
    def help_quit(self, line=None):
        help = \
'''quit: terminate interactive session

'''
        print help

    def do_EOF(self, *args):
        print ''
        sys.exit()

    def help_EOF(self, line=None):
        help = \
'''EOF: terminate interactive session

'''
        print help

    def do_exit(self, *args):
        print 'Use "quit" or Ctrl-D (i.e. EOF) to exit.'
        print ''


class UtilityRunner(object):

    usage  = """Usage: %prog [options] [command]"""

    # todo: Resolve having multiple definitions of this variable.
    systemName = 'domainmodel'
    utilityClass = AdministrationUtility

    def __init__(self, *args, **kwds):
        self.systemPath = ''
        self.environment = dm.environment.SystemEnvironment(self.systemName)
        self.configFilePathEnvironVariableName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.createOptionParser()
        self.createOptionParserOptions()
        self.parseArgs()
        self.concatenateArgs()
        if self.isHelpRequest():
            self.runUtilityOnce()
            return
        elif self.isVersionRequest():
            self.runUtilityOnce('about')
            return
        else:
            if self.options.config_file_path:
                filePath = os.path.abspath(self.options.config_file_path)
                os.environ[self.configFilePathEnvironVariableName] = filePath
            elif not os.environ.has_key(self.configFilePathEnvironVariableName):
                print 'ERROR. Please provide the path to the config file of' + \
                      ' the service you wish to administer\n\n'
                self.optionParser.print_help()
                sys.exit(1)
            if self.options.system_path:
                self.systemPath = self.options.system_path
            if self.isScriptRequest():
                self.runScript()
                return
            if self.isInteractiveRequest():
                errorStatus = self.runUtilityInteractive()
                sys.exit(errorStatus)
            elif len(self.args) > 0:
                errorStatus = self.runUtilityOnce(self.line)
                sys.exit(errorStatus)
            else:
                self.handleNullArgs()

    def handleNullArgs(self):
        self.optionParser.print_help()
        sys.exit(1)
 
    def createOptionParser(self):
        optionParserClass = optparse.OptionParser
        self.optionParser = optionParserClass(self.usage)
        
    def createOptionParserOptions(self):
        self.optionParser.add_option(
            '-i', '--interactive',
            action='store_true',
            dest='interactive',
            default=False,
            help='Run in interactive mode. If this option is' + \
                 ' specified any commands at invocation will be ignored.'
        )
        self.optionParser.add_option(
            '--version',
            action='store_true',
            dest='version',
            default=False,
            help='Display version information'
        )
        self.optionParser.add_option(
            '--config',
            action='store',
            dest='config_file_path',
            default='',
            help='Path to configuration file of service you wish to administer. ' + \
                 'If not defined defaults to environment variable ' + \
                 '%s if set.' % self.configFilePathEnvironVariableName
        )
        self.optionParser.add_option(
            '--system',
            action='store',
            dest='system_path',
            default=None,
            help='If you have installed the system to a path other\n' + \
                 ' than the default (sys.prefix) you need to specify\n' + \
                 ' the path provided at installation time here.'
        )
        self.optionParser.add_option(
            '-c', '--script',
            action='store_true',
            dest='script',
            default=False,
            help='Executes the admin script. Pass path as first argument.'
        )

    def parseArgs(self):
        (options, args) = self.optionParser.parse_args()
        self.options = options
        self.args = args

    def concatenateArgs(self):
        "Concatenates input arguments as one single-line string."
        argStrings = [str(arg) for arg in self.args]
        self.line = ' '.join(argStrings)

    def isHelpRequest(self):
        return len(self.args) > 0 and self.args[0] == 'help'
   
    def isVersionRequest(self):
        return self.options.version

    def isInteractiveRequest(self):
        return self.options.interactive

    def isScriptRequest(self):
        return self.options.script

    def runUtilityOnce(self, line=None):
        if line == None:
            line = self.line
        utility = self.createUtility()
        errorStatus = utility.onecmd(line)
        return errorStatus
        
    def runUtilityInteractive(self, line=None):
        if line == None:
            line = self.line
        utility = self.createUtility()
        errorStatus = utility.run_interactive()
        return errorStatus

    def createUtility(self):
        return self.utilityClass(self.options.system_path)

    def runScript(self):
        # todo: Generalise implementation in provide.cli.admin
        pass

