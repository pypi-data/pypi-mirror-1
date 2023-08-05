import unittest
import dm.testunit
import dm.dom.metatest
import dm.dom.accesscontroltest
import dm.dom.persontest

def suite():
    "Return a TestSuite of dm.db TestCases."
    suites = [
        dm.dom.metatest.suite(),
        dm.dom.accesscontroltest.suite(),
        dm.dom.persontest.suite(),
    ]
    return unittest.TestSuite(suites)

