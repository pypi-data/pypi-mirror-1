import unittest
from dm.view.testunit import TestCase
from dm.view.base import *
from dm.ioc import *
from dm.exceptions import *
from django.http import HttpRequest

def suite():
    suites = [
        unittest.makeSuite(TestSessionView),
        unittest.makeSuite(TestAbstractClassView),
        unittest.makeSuite(TestAbstractInstanceView),
        unittest.makeSuite(TestAbstractFormView),
        unittest.makeSuite(TestAbstractHasManyView),
        unittest.makeSuite(TestAbstractListView),
        unittest.makeSuite(TestAbstractSearchView),
        unittest.makeSuite(TestAbstractCreateView),
        unittest.makeSuite(TestAbstractReadView),
        unittest.makeSuite(TestAbstractUpdateView),
        unittest.makeSuite(TestAbstractDeleteView),
    ]
    return unittest.TestSuite(suites)


class MockView(ControlledAccessView):

    def assertActionObjectAuthorised(self, *args, **kwds):
        raise KforgePersonActionObjectDeclined

class MockSessionView(MockView, SessionView):
    pass

class MockAbstractClassView(MockView, AbstractClassView):
    pass

class MockAbstractInstanceView(MockView, AbstractInstanceView):
    pass

class MockAbstractFormView(MockView, AbstractFormView):
    pass

class MockAbstractHasManyView(MockView, AbstractHasManyView):
    pass

class MockAbstractListView(MockView, AbstractListView):
    pass

class MockAbstractSearchView(MockView, AbstractSearchView):
    pass

class MockAbstractCreateView(MockView, AbstractCreateView):
    pass

class MockAbstractReadView(MockView, AbstractReadView):
    pass

class MockAbstractUpdateView(MockView, AbstractUpdateView):
    pass

class MockAbstractDeleteView(MockView, AbstractDeleteView):
    pass


class ViewTestCase(TestCase):

    viewClass = None
    POST = {}
    requestPath = ''
    requiredResponseClassName = 'HttpResponse'
    requiredRedirect = ''
    requiredRedirectPath = ''

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.response = None
        self.request = self.buildRequest()
        self.view = self.buildView()
        self.failUnless(self.view)
        self.failUnless(self.view.dictionary, "No system dictionary.")
        self.failUnless(self.view.logger, "No logger.")

    def buildRequest(self):
        from django.http import HttpRequest
        request = HttpRequest()
        request.POST = self.POST
        request.path = self.requestPath
        return request

    def buildView(self):
        if not self.viewClass:
            raise "No viewClass set on test class %s" % self.__class__.__name__
        viewKwds = self.createViewKwds()
        return self.viewClass(**viewKwds)


    def createViewKwds(self):
        viewKwds = {}
        viewKwds['request'] = self.request
        return viewKwds

    def tearDown(self):
        self.view = None

    def test_getResponse(self):
        self.response = self.view.getResponse()
        self.failUnless(self.response, "No response?")
        self.failUnlessEqual(self.view.redirect, self.requiredRedirect)
        self.failUnlessEqual(self.view.redirectPath, self.requiredRedirectPath)
        self.failUnlessEqual(
            self.response.__class__.__name__,
            self.requiredResponseClassName,
            "%s != %s:\n\n%s" % (
                self.response.__class__.__name__,
                self.requiredResponseClassName,
                self.response,
            ),
        )


class TestSessionView(ViewTestCase):

    viewClass = MockSessionView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'

    def test_authoriseActionObject(self):
        object = None
#        self.failIf(self.view.authoriseActionObject('Read', object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.authoriseActionObject('Create', object))
#        self.failUnless(self.view.authoriseActionObject('Read', object))
#        self.failIf(self.view.authoriseActionObject('Update', object))
#        self.failIf(self.view.authoriseActionObject('Delete', object))

    def test_canRead(self):
        object = None
        self.failIf(self.view.canRead(object))
#        object = self.registry.getDomainClass('Project')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Member')
#        self.failUnless(self.view.canRead(object))
#        object = self.registry.getDomainClass('Service')
#        self.failUnless(self.view.canRead(object))

    def test_canCreate(self):
        object = None
        self.failIf(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Person')
#        self.failUnless(self.view.canCreate(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canCreate(object))

    def test_canUpdate(self):
        object = None
        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Person')
#        self.failIf(self.view.canUpdate(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canUpdate(object))

    def test_canDelete(self):
        object = None
        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Project')
#        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Person')
#        self.failIf(self.view.canDelete(object))
#        object = self.registry.getDomainClass('Member')
#        self.failIf(self.view.canDelete(object))



class TestAbstractClassView(ViewTestCase):

    viewClass = MockAbstractClassView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractInstanceView(ViewTestCase):

    viewClass = MockAbstractInstanceView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractFormView(ViewTestCase):

    viewClass = MockAbstractFormView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractHasManyView(ViewTestCase):

    viewClass = MockAbstractHasManyView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractListView(ViewTestCase):

    viewClass = MockAbstractListView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractSearchView(ViewTestCase):

    viewClass = MockAbstractSearchView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractCreateView(ViewTestCase):

    viewClass = MockAbstractCreateView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractReadView(ViewTestCase):

    viewClass = MockAbstractReadView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractUpdateView(ViewTestCase):

    viewClass = MockAbstractUpdateView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


class TestAbstractDeleteView(ViewTestCase):

    viewClass = MockAbstractDeleteView
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/login/'


