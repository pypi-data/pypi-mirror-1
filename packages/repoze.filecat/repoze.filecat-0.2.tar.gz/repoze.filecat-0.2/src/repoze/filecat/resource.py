import os
from mimetypes import guess_type

from zope import interface
from ore.xapian.interfaces import IIndexable

import interfaces

class FileSystemResource(object):
    interface.implements(IIndexable)

    __name__ = None
    __parent__ = None
    
    def __init__(self, path):
        self.path = path

    @property
    def mimetype(self):
        return guess_type(self.path)[0]

    def __repr__(self):
        return '<%s path="%s">' % \
               (type(self).__name__, self.path)

class ResourceLocator(object):
    interface.implements(interfaces.IResourceLocator)

    def __init__(self, path):
        self.path = path

    def get_path(self, resource):
        return os.path.join(self.path, resource.path)

