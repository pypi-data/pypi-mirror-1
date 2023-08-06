Filecat
=======

This is a WSGI application written for the ``repoze.bfg`` framework
which catalogs files in a Xapian database and provides a RESTful
interface to dispatch jobs and perform queries.

The application is configured with a ``path`` parameter which points
to a pool of files (a directory structure) and a ``host`` parameter
which provides a URL at which a webserver is configured to serve the
directory.

Components
----------

The main server thread starts up a Xapian connection and listens for
requests:

All queries are performed using the following HTTP API::

 method  path                           description
 ----------------------------------------------------------
  POST    /purge                        Clear index
  POST    /add                          Add file to index
  
          @path   Relative filename

  POST    /update                       Reindex file
  
          @path   Relative filename

  POST    /remove                       Remove file from index
  
          @path   Relative filename
         
  GET     /query                        Perform query
  
          Parameters are passed as-is
          to the Xapian query engine.
  

Query results
-------------

Queries return JSON structures with tuples of dicts on the following
form:

  @url       The URL where this file can be downloaded
  @mimetype  MIME-type of the file
  @metadata  Dict-like structure with mimetype-specific metadata*

*) The Hachoir Python package is used to provide this metadata for
 image and video files.


Credits
-------

Malthe Borch and Stefan Eletzhofer

