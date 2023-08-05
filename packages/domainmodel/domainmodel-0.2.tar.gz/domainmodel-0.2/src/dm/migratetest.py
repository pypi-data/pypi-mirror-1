import unittest
from dm.view.basetest import TestCase
from dm.migrate import DomainModelDumper
from dm.migrate import DomainModelLoader

def suite():
    suites = [
        unittest.makeSuite(TestDomainModelDumper),
        unittest.makeSuite(TestDomainModelLoader),
    ]
    return unittest.TestSuite(suites)


class TestDomainModelDumper(TestCase):

    def setUp(self):
        self.dumper = DomainModelDumper()

    def tearDown(self):
        del(self.dumper)

    def testDumpData(self):
        dump = self.dumper.dumpData()
        self.failUnless(dump['Action'])
        self.failUnless(dump['Action']['metaData'])
        self.failUnlessEqual(dump['Action']['metaData']['name'], 'String')
        self.failUnless(dump['Action'][1])
        self.failUnlessEqual(dump['Action'][1]['name'], 'Create')

    def testDumpDataAsJson(self):
        self.failUnless(self.dumper.dumpDataAsJson())

    def testDumpDataToFile(self):
        # get a file somewhere
        # call the dumpDataToFile() method with path to file
        # check the written file
        pass


class TestDomainModelLoader(TestCase):

    def setUp(self):
        self.loader = DomainModelLoader()

    def tearDown(self):
        del(self.loader)

    def testLoadDataAsJson(self):
        self.failIf('migrated' in self.registry.persons)
        self.loader.loadDataAsJson("""{
            "Person": {
                "metaData": {"name": "String"},
                "1": {"name": "migrated"}
            }
        }""")
        self.failUnless('migrated' in self.registry.persons)
        del(self.registry.persons['migrated'])
        self.failIf('migrated' in self.registry.persons)

        self.failIf('migrated' in self.registry.sessions)
        self.loader.loadDataAsJson("""{
            "Session": {
                "metaData": {"key": "String"},
                "1": {"key": "migrated"}
            }
        }""")
        self.failUnless('migrated' in self.registry.sessions)
        del(self.registry.sessions['migrated'])
        self.failIf('migrated' in self.registry.sessions)

