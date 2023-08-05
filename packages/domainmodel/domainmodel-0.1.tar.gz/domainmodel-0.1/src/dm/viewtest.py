import unittest
import dm.view.manipulatortest
import dm.view.basetest
import dm.view.admintest
import dm.view.registrytest

def suite():
    suites = [
        dm.view.manipulatortest.suite(),
        dm.view.basetest.suite(),
        dm.view.admintest.suite(),
        dm.view.registrytest.suite(),
    ]
    return unittest.TestSuite(suites)

