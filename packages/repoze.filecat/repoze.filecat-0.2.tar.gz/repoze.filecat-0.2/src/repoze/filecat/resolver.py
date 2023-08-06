import os
import resource

from zope import interface
from ore.xapian.interfaces import IResolver

class FileSystemResolver(object):
    interface.implements(IResolver)
    scheme = ""

    def __init__(self, path):
        self.path = path

    def id(self, resource):
        return resource.path

    def resolve(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.path, path)
        return resource.FileSystemResource(path)
