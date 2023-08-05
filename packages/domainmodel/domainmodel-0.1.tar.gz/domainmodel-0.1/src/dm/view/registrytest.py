import unittest
from dm.view.basetest import ViewTestCase
from dm.view.registry import RegistryView
from dm.view.registry import RegistryListView
from dm.view.registry import RegistrySearchView
from dm.view.registry import RegistryCreateView
from dm.view.registry import RegistryReadView
from dm.view.registry import RegistryUpdateView
from dm.view.registry import RegistryDeleteView

def suite():
    suites = [
        unittest.makeSuite(TestRegistryView),
        unittest.makeSuite(TestRegistryListView),
        unittest.makeSuite(TestRegistrySearchView),
        unittest.makeSuite(TestRegistrySearchView2),
        unittest.makeSuite(TestRegistryCreateView),
        unittest.makeSuite(TestRegistryReadView),
        unittest.makeSuite(TestRegistryUpdateView),
        unittest.makeSuite(TestRegistryDeleteView),
    ]
    return unittest.TestSuite(suites)


class MockRegistryView(RegistryView):
    templatePath = 'index'

class MockRegistryListView(MockRegistryView, RegistryListView):
    pass

class MockRegistrySearchView(MockRegistryView, RegistrySearchView):
    pass

class MockRegistryCreateView(MockRegistryView, RegistryCreateView):
    pass

class MockRegistryReadView(MockRegistryView, RegistryReadView):
    pass

class MockRegistryUpdateView(MockRegistryView, RegistryUpdateView):
    pass

class MockRegistryDeleteView(MockRegistryView, RegistryDeleteView):
    pass


class RegistryViewTestCase(ViewTestCase):
    
    registryPath = 'persons'
    requiredActionName = ''

    def createViewKwds(self):
        viewKwds = super(RegistryViewTestCase, self).createViewKwds()
        viewKwds['registryPath'] = self.registryPath
        return viewKwds

    def test_actionName(self):
        self.failUnlessEqual(self.view.actionName, self.requiredActionName)

    def test_getViewPosition(self):
        self.failUnlessEqual(self.view.getViewPosition(), "persons/list")


class TestRegistryView(RegistryViewTestCase):
    viewClass = MockRegistryView

class TestRegistryListView(RegistryViewTestCase):
    viewClass = MockRegistryListView

class TestRegistrySearchView(RegistryViewTestCase):

    viewClass = MockRegistrySearchView
    userQuery = 'admin'
    POST = {
        'userQuery': userQuery,
    }

    def test_getResponse(self):
        super(TestRegistrySearchView, self).test_getResponse()
        self.failUnless(self.view.context['domainObjectList'])
        self.failUnlessEqual(self.view.userQuery, self.userQuery)
        self.failUnlessEqual(self.view.context['userQuery'], self.userQuery)
        self.failUnlessEqual(self.view.context['resultsCount'], 1)
        self.failUnlessEqual(self.view.context['isResultSingular'], True)
    
    def test_searchManipulatedRegister(self):
        self.view.userQuery = 'adm'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 1)
        self.failUnless(
            hasattr(results[0], 'name'),
            "No name attribute on object '%s' in results '%s'" % (
                str(results[0]),
                str(results),
            )
        )
        self.failUnlessEqual(results[0].name, 'admin')
        self.view.userQuery = 'vis'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 1)
        self.failUnlessEqual(results[0].name, 'visitor')
        self.view.userQuery = 'i'
        results = self.view.searchManipulatedRegister()
        self.failUnlessEqual(len(results), 3)

class TestRegistrySearchView2(RegistryViewTestCase):

    viewClass = MockRegistrySearchView
    startsWith = 'ad'
    POST = {
        'startsWith': startsWith,
    }

    def test_getResponse(self):
        super(TestRegistrySearchView2, self).test_getResponse()
        self.failUnless(self.view.context['domainObjectList'])
        self.failUnlessEqual(self.view.startsWith, self.startsWith)
        self.failUnlessEqual(self.view.context['startsWith'], self.startsWith)
        self.failUnlessEqual(self.view.context['resultsCount'], 1)
        self.failUnlessEqual(self.view.context['isResultSingular'], True)


class TestRegistryCreateView(RegistryViewTestCase):
    viewClass = MockRegistryCreateView

class TestRegistryReadView(RegistryViewTestCase):
    viewClass = MockRegistryReadView
    registryPath = 'persons/admin'

class TestRegistryUpdateView(RegistryViewTestCase):
    viewClass = MockRegistryUpdateView
    registryPath = 'persons/admin'

class TestRegistryDeleteView(RegistryViewTestCase):
    viewClass = MockRegistryDeleteView
    registryPath = 'persons/admin'

