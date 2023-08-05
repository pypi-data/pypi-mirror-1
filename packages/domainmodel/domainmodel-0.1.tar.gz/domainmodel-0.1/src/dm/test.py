import unittest
import dm.environmenttest
import dm.logtest
import dm.debugtest
import dm.dbtest
import dm.domtest
import dm.plugintest
import dm.ioctest
import dm.configtest
import dm.dictionarytest
import dm.commandtest
import dm.filesystemtest
import dm.accesscontroltest
import dm.applicationtest
import dm.viewtest
from dm.testunit import ApplicationTestSuite

def suite():
    suites = [
        dm.environmenttest.suite(),
        dm.logtest.suite(),
        dm.debugtest.suite(),
        dm.dbtest.suite(),
        dm.domtest.suite(),
        dm.plugintest.suite(),
        dm.ioctest.suite(),
        dm.configtest.suite(),
        dm.dictionarytest.suite(),
        dm.commandtest.suite(),
        #dm.filesystemtest.suite(),
        dm.accesscontroltest.suite(),
        dm.viewtest.suite(),
        dm.applicationtest.suite(),
    ]
    return ApplicationTestSuite(suites)

