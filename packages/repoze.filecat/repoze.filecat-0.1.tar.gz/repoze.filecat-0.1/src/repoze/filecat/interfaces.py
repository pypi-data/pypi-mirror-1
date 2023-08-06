from zope import interface

class IResourceLocator(interface.Interface):
    def get_path(resource):
        """Returns an absolute path for a resource."""

class IXapianConnection(interface.Interface):
    """ utility to fetch thread-local xapian connections. """

    def get_connection():
        """ return xapian connection. """

