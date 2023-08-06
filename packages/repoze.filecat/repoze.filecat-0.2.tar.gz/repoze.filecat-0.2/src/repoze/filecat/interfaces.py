from zope import interface

class IResourceLocator(interface.Interface):
    def get_path(resource):
        """Returns an absolute path to a resource."""

class IXapianConnection(interface.Interface):
    """Utility to fetch thread-local xapian connections. """

    def get_connection():
        """ return xapian connection."""
