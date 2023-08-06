import os

from zope import interface
from zope import component

import zope.configuration.xmlconfig 
import ore.xapian.interfaces
import ore.xapian.search
import ore.xapian.queue

from repoze.filecat.interfaces import IXapianConnection
from repoze.bfg import registry
from repoze.filecat import resource
from repoze.filecat import index
from repoze.filecat import resolver

xapian_config_path = os.path.join(
    os.path.dirname(__file__), 'xapian.zcml')

def directory_watcher(path):
    import repoze.filecat.watch
    return repoze.filecat.watch.start(path, 3)

def xapian_config(path, database, observer_factory=directory_watcher):
    # globally register xapian utilities for indexing thread.  This thread runs
    # outside the WSGI app and thus uses the **global** component registry
    registry.registry_manager.push(component.globalregistry.base)

    import repoze.filecat
    zope.configuration.xmlconfig.XMLConfig(xapian_config_path, repoze.filecat)()

    # provide resource locator and resolver
    component.provideUtility(resource.ResourceLocator(path))
    component.provideUtility(resolver.FileSystemResolver(path))
    
    # reset registry manager
    registry.registry_manager.pop()

    database_not_exists = not os.path.exists(database)
    
    # start indexer queue
    ore.xapian.queue.QueueProcessor.POLL_TIMEOUT = 0.1
    ore.xapian.queue.QueueProcessor.FLUSH_THRESHOLD = 1
    ore.xapian.queue.QueueProcessor.start(index.create_indexer(database))

    observer = observer_factory(path)
    if database_not_exists:
        observer.clear()

class Connection(object):
    interface.implements(IXapianConnection)

    def __init__(self, database):
        self.database = database
        self.connections = ore.xapian.search.ConnectionHub(database)

    def get_connection(self):
        return self.connections.get()


