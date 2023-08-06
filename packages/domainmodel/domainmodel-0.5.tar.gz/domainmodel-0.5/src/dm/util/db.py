import os
import commands

import dm.ioc
from dm.dictionarywords import DB_DELETE_COMMAND, DB_CREATE_COMMAND

class Database(object):
    """Manipulate system service database.

    As some of these methods must function when the database does not exist it
    is important that the features used are highly restricted so as to ensure
    that a dependency on the database is not created.
    """

    features = dm.ioc.features

    # name of commands in system dictionary
    createCommandName = 'db.create_command'
    deleteCommandName = 'db.delete_command'

    def _registerSystemDictionaryFeature(self):
        self.didRegistration = False
        if not 'SystemDictionary' in self.features:
            systemDictionary = self._getSystemDictionary()
            self.features.register('SystemDictionary', systemDictionary)
            self.didRegistration = True
    
    def _getSystemDictionary(self):
        # override in derived classes
        import dm.dictionary
        systemDictionary = dm.dictionary.SystemDictionary()
        return systemDictionary

    def _deregisterSystemDictionaryFeature(self):
        if self.didRegistration:
            self.features.deregister('SystemDictionary')
   
    def _runCommand(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = 'Could not execute command\n\t[%s]\n\nReason: %s' \
                    % (cmd, output)
            raise(Exception(msg))

    def _runCommandFromDictionary(self, commandName):
        self._registerSystemDictionaryFeature()
        self.dictionary = self.features['SystemDictionary']
        cmd = self.dictionary[commandName]
        # deregister before running command as command may raise exception
        self._deregisterSystemDictionaryFeature()
        self._runCommand(cmd)

    def create(self):
        "Create a service database."
        self._runCommandFromDictionary(DB_CREATE_COMMAND)

    def delete(self):
        "Delete a service database."
        self._runCommandFromDictionary(DB_DELETE_COMMAND)

    def rebuild(self):
        """Rebuild service database (delete + create + init)
        Allow for possibility that database does not already exist.
        """
        try:
            self.delete()
        except Exception, inst: # allow for non-existence of database
            msg = \
'''\nDatabase.rebuild(): error on attempt to delete db. This need *not*
indicate a problem but simply that the db does not exist. Please check the
following error message for details:
    
%s'''  % inst
            print(msg)
        self.create()
        self.init()

    def init(self):
        """
        Initialises service database by creating initial domain object records.
        """
        initModelCommandClass = self.getInitModelCommandClass()
        initModelCommand = initModelCommandClass()
        initModelCommand.execute()

    def getInitModelCommandClass(self):
        commandSet = self.getApplicationCommandSet()
        return commandSet['InitialiseDomainModel']

    def getApplicationCommandSet(self):
        import dm.soleInstance
        commandSet = dm.soleInstance.application.commands
        return commandSet

