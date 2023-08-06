from zope import interface

from ore.xapian.interfaces import IResolver

import resource

class FileSystemResolver(object):
    interface.implements(IResolver)
    scheme = ""

    def id(self, resource):
        return resource.path

    def resolve(self, path):
        return resource.FileSystemResource(path)

file_system_resolver = FileSystemResolver()
