import os

from zope import component
import zope.configuration.xmlconfig 

from repoze.bfg import router
from repoze.bfg import urldispatch
from repoze.bfg import security

from repoze import filecat

import ore.xapian.queue

from interfaces import IXapianConnection

import index
import xapian
import resolver


class RoutesContext(object):
    __acl__ = [
            (security.Allow, security.Everyone, 'view'),
            ]

    def __init__(self, controller, host, path):
        self.controller = controller
        self.path = path
        self.host = host


xapian_config = os.path.join(
    os.path.dirname(__file__), 'xapian.zcml')


def make_app(global_config, path=None, host=None, database=None):

    def context_factory(controller, **kw):
        return RoutesContext(controller, host, path)

    # set up routes root
    root = urldispatch.RoutesMapper(lambda x: {})
    root.connect('purge',  controller='purge',  context_factory=context_factory)
    root.connect('add',    controller='add',    context_factory=context_factory)
    root.connect('update', controller='update', context_factory=context_factory)
    root.connect('remove', controller='remove', context_factory=context_factory)
    root.connect('query',  controller='query',  context_factory=context_factory)

    # globally register xapian utilities for indexing thread.  This thread runs
    # outside the WSGI app and thus uses the **global** component registry
    import repoze.filecat
    zope.configuration.xmlconfig.XMLConfig( xapian_config, repoze.filecat)()

    # provide resource locator
    import resource
    component.provideUtility(resource.ResourceLocator(path))

    # start indexer queue
    ore.xapian.queue.QueueProcessor.POLL_TIMEOUT = 0.1
    ore.xapian.queue.QueueProcessor.FLUSH_THRESHOLD = 1
    ore.xapian.queue.QueueProcessor.start(index.create_indexer(database))

    # startup directory observer
    import watch
    watch.start(path, 3)


    app = router.make_app(root, filecat)

    ###
    # register local components

    # provide xapian connection utility
    app.registry.registerUtility(xapian.Connection(database))


    return app

if __name__ == '__main__':
    from paste import httpserver
    app = make_app(None)
    httpserver.serve(app, host='0.0.0.0', port='5431')
    
