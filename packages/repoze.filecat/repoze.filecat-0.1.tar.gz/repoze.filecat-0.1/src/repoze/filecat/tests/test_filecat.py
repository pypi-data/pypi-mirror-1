import unittest
import time
import os

from zope import interface
from zope import component

import zope.component.testing
import zope.configuration.xmlconfig

import ore.xapian.queue
import ore.xapian.interfaces
import ore.xapian.search

import repoze.filecat.tests

import transaction

from repoze.filecat import xapian

static_path = os.path.join(
    os.path.dirname(repoze.filecat.tests.__file__), 'static')

class ViewTests(unittest.TestCase):
    def setUp(self):
        from repoze.filecat import resource

        zope.component.testing.setUp(self)
        self.operation_queue = operation_queue = []

        class MockOperationFactory(object):
            component.adapts(ore.xapian.interfaces.IIndexable)
            interface.implements(ore.xapian.interfaces.IOperationFactory)

            def __init__(self, resource):
                self.resource = resource

            def add(self):
                operation_queue.append(('add', self.resource))
            def modify(self):
                operation_queue.append(('modify', self.resource))
            def remove(self):
                operation_queue.append(('remove', self.resource))

        component.provideAdapter(MockOperationFactory)

    def tearDown(self):
        zope.component.testing.tearDown(self)
        del self.operation_queue[:]

    def test_purge_view(self):
        """Purge view."""

        from repoze.filecat.views import purge_view
        request = DummyRequest(params={'message':'abc'})
        context = DummyContext()
        purge_view(context, request)

    def test_add_view(self):
        """Add file to index using view."""

        from repoze.filecat.views import add_view
        request = DummyRequest(params={'path': 'fashion.jpg'})
        context = DummyContext()
        add_view(context, request)

        self.assertEqual(len(self.operation_queue), 1)        
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'add')
        self.assertEqual(resource.path, request.params.get('path'))

    def test_add_view_missing(self):
        """Add view raises HTTP not found if path does not exist."""

        from repoze.filecat.views import add_view
        from webob.exc import HTTPNotFound

        context = DummyContext()
        request = DummyRequest(params={'path': 'missing.jpg'})
        self.assertRaises(HTTPNotFound, lambda: add_view(context, request))

    def test_update_view(self):
        """Update a file already indexed."""

        from repoze.filecat.views import update_view
        request = DummyRequest(params={'path': 'fashion.jpg'})
        context = DummyContext()
        update_view(context, request)

        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'modify')
        self.assertEqual(resource.path, request.params.get('path'))

    def test_remove_view(self):
        """Remove file from index."""

        from repoze.filecat.views import remove_view
        request = DummyRequest(params={'path': 'fashion.jpg'})
        context = DummyContext()
        remove_view(context, request)

        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'remove')
        self.assertEqual(resource.path, request.params.get('path'))


class IndexingTests(unittest.TestCase):
    def setUp(self):
        from repoze.filecat import index
        from repoze.filecat import resource

        zope.component.testing.setUp(self)
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', repoze.filecat)()

        ore.xapian.queue.QueueProcessor.POLL_TIMEOUT = 0.1
        ore.xapian.queue.QueueProcessor.FLUSH_THRESHOLD = 1
        self.indexer = index.create_indexer('tmp.idx')
        ore.xapian.queue.QueueProcessor.start(self.indexer)
        self.connections = ore.xapian.search.ConnectionHub('tmp.idx')

        locator = resource.ResourceLocator(static_path)
        component.provideUtility(locator)

        self.resource = resource.FileSystemResource('fashion.jpg')

    def tearDown(self):
        ore.xapian.queue.QueueProcessor.stop()

        # indexer cleanup
        for name in self.indexer.iterids():
            self.indexer.delete(name)

        self.indexer.flush()
        self.indexer.close()

        zope.component.testing.tearDown(self)

    def test_index_image_verify(self):
        """Index image and verify index."""

        from repoze.filecat import resolver

        # index image
        ore.xapian.interfaces.IOperationFactory(self.resource).add()
        transaction.commit()
        time.sleep(1)

        # query to verify
        searcher = self.connections.get()
        query = searcher.query_all()
        results = tuple(searcher.search(query, 0, 30))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, resolver.file_system_resolver.id(self.resource))

    def test_index_image_metadata(self):
        """Image metadata query."""

        from repoze.filecat import resolver

        # index image
        ore.xapian.interfaces.IOperationFactory(self.resource).add()
        transaction.commit()
        time.sleep(1)

        # query to verify
        searcher = self.connections.get()
        query = searcher.query_parse("New York")
        results = tuple(searcher.search(query, 0, 30))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, resolver.file_system_resolver.id(self.resource))

        # search tag (always lowercase)
        query = searcher.query_field('keywords', "new york")
        results = tuple(searcher.search(query, 0, 30, gettags='keywords'))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, resolver.file_system_resolver.id(self.resource))


class QueryTests(unittest.TestCase):

    def setUp(self):
        from repoze.filecat.interfaces import IXapianConnection

        zope.component.testing.setUp(self)
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', repoze.filecat)()

        class MockSearcher(object):
            OP_OR=1
            def query_composite(self, op, queries):
                pass
            def query_all(self):
                pass

            def search(self, query, *args, **kw):
                class Brain(object):
                    def __init__(self, id, **kw):
                        self.id = id
                        self.data = kw
                return (
                        Brain("foo.jpg", author="alfred e. neuman", date="2008-09-30"),
                        Brain("bar.jpg", author="fred kaputnik", date="2008-10-01"),
                        )

        class MockConnection(object):
            interface.implements(IXapianConnection)
            def get_connection(self):
                return MockSearcher()

        component.provideUtility(MockConnection())

    def tearDown(self):
        zope.component.testing.tearDown(self)

    def test_query_view(self):
        """Test the query view."""

        from repoze.filecat.views import query_view
        from repoze.filecat.json import JSONResponse
        import jsonlib
        from webob.exc import HTTPNotFound

        # setup request and context
        context = DummyContext()
        request = DummyRequest(params={'keywords': 'New York'})

        # perform query
        response = query_view(context, request)

        # we expect a JSON response
        self.assertEqual(isinstance(response, JSONResponse), True)

        # the body must be valid JSON
        self.failUnless(jsonlib.read(response.body))

        # we expect results JSON encoded
        results = jsonlib.read(response.body)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("url"), "http://localhost:8080/static/foo.jpg")
        self.assertEqual(results[1].get("url"), "http://localhost:8080/static/bar.jpg")
        self.assertEqual(results[0].get("mimetype"), "image/jpeg")


class ObserverOperationTest(unittest.TestCase):

    def setUp(self):
        from repoze.filecat.interfaces import IXapianConnection

        zope.component.testing.setUp(self)
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', repoze.filecat)()

        self.operation_queue = operation_queue = []
        class MockOperationFactory(object):
            component.adapts(ore.xapian.interfaces.IIndexable)
            interface.implements(ore.xapian.interfaces.IOperationFactory)

            def __init__(self, resource):
                self.resource = resource

            def add(self):
                operation_queue.append(('add', self.resource))
            def modify(self):
                operation_queue.append(('modify', self.resource))
            def remove(self):
                operation_queue.append(('remove', self.resource))

        component.provideAdapter(MockOperationFactory)

        self.path = "some/folder/foo.jpg"

    def tearDown(self):
        zope.component.testing.tearDown(self)
        del self.operation_queue[:]

    def test_callback_add(self):
        """ test the cb used by the dir watch daemon thread """

        from repoze.filecat.watch import op_callback

        # call the call back for an "add" event
        op_callback("added", self.path)
        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'add')
        self.assertEqual(resource.path, self.path)

    def test_callback_remove(self):
        """ test the cb used by the dir watch daemon thread """

        from repoze.filecat.watch import op_callback

        # call the call back for an "add" event
        op_callback("removed", self.path)
        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'remove')
        self.assertEqual(resource.path, self.path)

    def test_callback_changed(self):
        """ test the cb used by the dir watch daemon thread """

        from repoze.filecat.watch import op_callback

        # call the call back for an "add" event
        op_callback("changed", self.path)
        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'modify')
        self.assertEqual(resource.path, self.path)


class ObserverTest(unittest.TestCase):

    def setUp(self):
        from repoze.filecat import watch

        self.rel_path = "%s.jpg" % self.__class__.__name__
        self.path = os.path.join(static_path, self.rel_path)
        if os.path.exists(self.path):
            os.unlink(self.path)

        # simple callback for tests
        self.events = events = []
        def callback(evt, path):
            events.append((evt, path))

        # get an observer.  
        self.observer = watch.DirectoryChangeObserver(static_path, callback)

        # mock ticker such that we can call the observer
        def ticker():
            yield 0
        self.observer.ticker = ticker


    def tearDown(self):
        del self.events[:]
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_observer(self):
        """ test the observer """
        self.failUnless(self.path not in self.observer.before)

        # add a file
        file(self.path,"w").write("foo")

        self.observer()
        self.assertEqual(len(self.events), 1 )
        self.assertEqual(self.events[0], ("added", self.rel_path))

        # modify file
        file(self.path,"a").write("bar")
        self.observer.before[self.path] = 0 # force MTIME

        self.observer()
        self.assertEqual(len(self.events), 2 )
        self.assertEqual(self.events[1], ("changed", self.rel_path))

        # remove
        os.unlink(self.path)

        self.observer()
        self.assertEqual(len(self.events), 3)
        self.assertEqual(self.events[2], ("removed", self.rel_path))


class DummyContext:
    path = static_path
    host = "http://localhost:8080/static"


class DummyRequest:
    application_url = 'http://app'
    def __init__(self, environ=None, params=None):
        if environ is None:
            environ = {}
        self.environ = environ
        if params is None:
            params = {}
        self.params = params


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ViewTests))
    suite.addTest(unittest.makeSuite(IndexingTests))
    suite.addTest(unittest.makeSuite(QueryTests))
    suite.addTest(unittest.makeSuite(ObserverTest))
    suite.addTest(unittest.makeSuite(ObserverOperationTest))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
