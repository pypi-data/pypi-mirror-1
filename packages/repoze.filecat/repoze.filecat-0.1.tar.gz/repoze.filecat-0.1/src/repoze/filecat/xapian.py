from zope import interface

import ore.xapian.interfaces
import ore.xapian.search

from interfaces import IXapianConnection

class Connection(object):
    interface.implements(IXapianConnection)

    def __init__(self, database):
        self.database = database
        self.connections = ore.xapian.search.ConnectionHub(database)

    def get_connection(self):
        return self.connections.get()


