Filecat
=======

This package provides application support for indexing and serving
content in a file system.

An HTTP API is available for querying operations.

Setup
-----

The Xapian database queue processor must be configured with an
indexer which points to a database file on disk, e.g.::

  >>> indexer = repoze.filecat.index.create_indexer(db_path)
  >>> ore.xapian.queue.QueueProcessor.start(indexer)

To start the directory observer (configured to scan every 3 seconds)::

  >>> repoze.filecat.watch.start(directory, 3)

We can then query the Xapian database by opening a connection::

  >>> connection = xapian.Connection(db_path)

Formats
-------

Currently supported file formats:

- JPEG (image/jpeg)
- ReStructuredText (text/x-rst)
  
Authors
-------

Malthe Borch <mborch@gmail.com>
Stefan Eletzhofer <stefan.eletzhofer@inquant.de>
Robert Marianski <rmarianski@gmail.com>

Application
===========

The filecat server application is configured with a ``path`` parameter
which points to a pool of files (a directory structure) and a ``host``
parameter which provides a URL at which a webserver is configured to
serve up the directory as static files.

API
---

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

Results
-------

Queries return a JSON structure which is first a two-tuple
(matches_estimated, results). The result set is a tuple of dicts:

  @url       The URL where this file can be downloaded
  @mimetype  MIME-type of the file
  @metadata  Dict-like structure with mimetype-specific metadata*



