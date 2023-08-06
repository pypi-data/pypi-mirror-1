import transaction
import unittest
import datetime
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
from repoze.bfg.interfaces import IRoutesMapper

static_path = os.path.join(
    os.path.dirname(repoze.filecat.tests.__file__), 'static')

class DummyRoutesMapper(object):
    def connect(self, *args, **kwargs):
        pass

class ViewTests(unittest.TestCase):
    def setUp(self):
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
        try:
            purge_view(context, request)
        except NotImplementedError:
            pass

    def test_add_view(self):
        """Add file to index using view."""

        from repoze.filecat.views import add_view
        request = DummyRequest(params={'path': 'sample.jpg'})
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
        request = DummyRequest(params={'path': 'sample.jpg'})
        context = DummyContext()
        update_view(context, request)

        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'modify')
        self.assertEqual(resource.path, request.params.get('path'))

    def test_remove_view(self):
        """Remove file from index."""

        from repoze.filecat.views import remove_view
        request = DummyRequest(params={'path': 'sample.jpg'})
        context = DummyContext()
        remove_view(context, request)

        self.assertEqual(len(self.operation_queue), 1)
        operation, resource = self.operation_queue[0]
        self.assertEqual(operation, 'remove')
        self.assertEqual(resource.path, request.params.get('path'))

class ExtractionTests(unittest.TestCase):
    @property
    def jpeg_stream(self):
        return open(os.path.join(static_path, 'sample.jpg'), 'rb')

    @property
    def rst_stream(self):
        return open(os.path.join(static_path, 'sample.rst'), 'rb')

    def test_xmp_metadata(self):
        from repoze.filecat import extraction
        metadata = extraction.extract_xmp_from_jpeg(self.jpeg_stream)

        # verify that this photograph was manipulated with Photoshop
        description = metadata.xpath(
            './/rdf:Description', namespaces=
            {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'})[0]
        
        self.assertEqual(
            description.attrib.get('{http://ns.adobe.com/xap/1.0/}CreatorTool'),
            "Adobe Photoshop CS Macintosh")

    def test_rst_metadata(self):
        from repoze.filecat import extraction
        metadata = extraction.extract_dc_from_rst(self.rst_stream)

        self.assertEqual(metadata['title'], u"Restructuredtext-Test-Directive")
        self.assertEqual(metadata['author'], u"David Goodger")
        self.assertEqual(metadata['creation_date'], datetime.date(2009, 8, 17))

class IndexingTests(unittest.TestCase):
    def setUp(self):
        ore.xapian.interfaces.DEBUG_SYNC = True

        from repoze.filecat import index
        from repoze.filecat import resource

        zope.component.testing.setUp(self)

        from zope.component import getSiteManager
        gsm = getSiteManager()
        gsm.registerUtility(DummyRoutesMapper(), IRoutesMapper)
        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', repoze.filecat)()

        ore.xapian.queue.QueueProcessor.POLL_TIMEOUT = 0.1
        ore.xapian.queue.QueueProcessor.FLUSH_THRESHOLD = 1
        self.indexer = index.create_indexer('tmp.idx')
        ore.xapian.interfaces.DEBUG_SYNC_IDX = self.indexer
        
        ore.xapian.queue.QueueProcessor.start(self.indexer)
        self.connections = ore.xapian.search.ConnectionHub('tmp.idx')

        locator = resource.ResourceLocator(static_path)
        component.provideUtility(locator)

        self.jpeg_resource = resource.FileSystemResource('sample.jpg')
        self.rst_resource = resource.FileSystemResource('sample.rst')

        from repoze.filecat.resolver import FileSystemResolver
        self.resolver = FileSystemResolver(static_path)
        component.provideUtility(self.resolver)
        
    def tearDown(self):
        ore.xapian.queue.QueueProcessor.stop()

        # indexer cleanup
        for name in self.indexer.iterids():
            self.indexer.delete(name)

        self.indexer.flush()
        self.indexer.close()

        zope.component.testing.tearDown(self)

    # JPEG

    def test_jpeg_indexer(self):
        from repoze.filecat import index
        indexer = index.Indexer(self.jpeg_resource)

        document = indexer.document()
        metadata = dict(
            (field.name, field.value) for field in document.fields)

        self.assertEqual(
            metadata.get('creation_date'), datetime.datetime(2008, 9, 3, 18, 19, 22, 2))
        self.assertEqual(
            metadata.get('short_name'), u"sample")
        
    def test_jpeg_query(self):
        # index image
        ore.xapian.interfaces.IOperationFactory(self.jpeg_resource).add()
        transaction.commit()
        time.sleep(1)

        # query to verify
        searcher = self.connections.get()
        query = searcher.query_parse("kate")
        results = tuple(searcher.search(query, 0, 30))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, self.resolver.id(self.jpeg_resource))

        # search tag (always lowercase)
        query = searcher.query_field('keywords', "kate moss")
        results = tuple(searcher.search(query, 0, 30, gettags='keywords'))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, self.resolver.id(self.jpeg_resource))

    # ReStructured Text

    def test_rst_indexer(self):
        from repoze.filecat import index
        indexer = index.Indexer(self.rst_resource)

        document = indexer.document()
        metadata = dict(
            (field.name, field.value) for field in document.fields)

        self.assertEqual(
            metadata.get('creation_date'), datetime.date(2009, 8, 17))
        self.assertEqual(
            metadata.get('short_name'), u"restructuredtext-test-directive")

    def test_rst_query(self):
        # index image
        ore.xapian.interfaces.IOperationFactory(self.rst_resource).add()
        transaction.commit()
        time.sleep(1)

        # query to verify
        searcher = self.connections.get()
        query = searcher.query_parse("admonitions")
        results = tuple(searcher.search(query, 0, 30))

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].id, self.resolver.id(self.rst_resource))

class QueryTests(unittest.TestCase):

    def setUp(self):
        from repoze.filecat.interfaces import IXapianConnection

        zope.component.testing.setUp(self)
        from zope.component import getSiteManager
        gsm = getSiteManager()
        gsm.registerUtility(DummyRoutesMapper(), IRoutesMapper)

        zope.configuration.xmlconfig.XMLConfig(
            'configure.zcml', repoze.filecat)()

        class MockSearcher(object):
            OP_OR=1
            def query_composite(self, op, queries):
                pass
            
            def query_all(self):
                pass

            def search(self, query, start, limit, *args, **kw):
                class Brain(object):
                    def __init__(self, id, **kw):
                        self.id = id
                        self.data = kw

                results = Brain("foo.jpg", author="alfred e. neuman", date="2008-09-30"), \
                          Brain("bar.jpg", author="fred kaputnik", date="2008-10-01")

                return MockSearchResults(results[start:start+limit], 2)

            @property
            def matches_estimated(self):
                return 2

        class MockSearchResults(tuple):
            def __new__(cls, results, matches_estimated):
                inst = tuple.__new__(cls, results)
                inst.matches_estimated = matches_estimated
                return inst
            
        class MockConnection(object):
            interface.implements(IXapianConnection)
            def get_connection(self):
                return MockSearcher()

        component.provideUtility(MockConnection())

        from repoze.filecat.resolver import FileSystemResolver
        self.resolver = FileSystemResolver(static_path)
        component.provideUtility(self.resolver)

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
        request = DummyRequest(
            params={'keywords': 'New York'})

        # perform query
        response = query_view(context, request)

        # we expect a JSON response
        self.assertEqual(isinstance(response, JSONResponse), True)

        # the body must be valid JSON
        self.failUnless(jsonlib.read(response.body))

        # we expect results JSON encoded
        matches, results = jsonlib.read(response.body)
        self.assertEqual(matches, 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("url"), "http://localhost:8080/static/foo.jpg")
        self.assertEqual(results[1].get("url"), "http://localhost:8080/static/bar.jpg")
        self.assertEqual(results[0].get("mimetype"), "image/jpeg")


class ObserverOperationTest(unittest.TestCase):

    def setUp(self):
        zope.component.testing.setUp(self)
        
        from zope.component import getSiteManager
        gsm = getSiteManager()
        gsm.registerUtility(DummyRoutesMapper(), IRoutesMapper)
        
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
        self.failUnless(self.path not in self.observer.files)

        # add a file
        file(self.path,"w").write("foo")

        self.observer()
        self.assertEqual(len(self.events), 1 )
        self.assertEqual(self.events[0], ("added", self.rel_path))

        # modify file
        file(self.path,"a").write("bar")
        self.observer.files[self.path] = 0 # force MTIME

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
    suite.addTest(unittest.makeSuite(ExtractionTests))
    suite.addTest(unittest.makeSuite(IndexingTests))
    suite.addTest(unittest.makeSuite(QueryTests))
    suite.addTest(unittest.makeSuite(ObserverTest))
    suite.addTest(unittest.makeSuite(ObserverOperationTest))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
