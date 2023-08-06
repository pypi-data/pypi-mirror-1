import os
import transaction

from zope import component
from webob.exc import HTTPNotFound
from ore.xapian.interfaces import IOperationFactory
from ore.xapian.interfaces import IResolver
from repoze.filecat.resource import FileSystemResource
from repoze.filecat.json import JSONResponse
from repoze.filecat.index import search

def get_path(context, request, _raise=True):
    relative_path = request.params.get('path')
    if relative_path is None:
        raise ValueError("Must provide ``path``.")

    absolute_path = os.path.join(context.path, relative_path)
    if not os.path.exists(absolute_path) and _raise:
        raise HTTPNotFound

    return relative_path, absolute_path

def add_view(context, request):
    """ add view

    Add a file to the index.  The path of the file is taken from the request.
    The path is assumed to be *relative* to the file pool.

    @context    This is a ``RoutesContext`` instance
    @request    A webob request object
    """
    relative_path, absolute_path = get_path(context, request)

    # ADD
    IOperationFactory(FileSystemResource(
        relative_path)).add()

    transaction.commit()
    return JSONResponse({})

def update_view(context, request):
    """ update view

    Update a file already in the index.  The path of the file is taken from the
    request.  The path is assumed to be *relative* to the file pool.

    @context    This is a ``RoutesContext`` instance
    @request    A webob request object
    """
    relative_path, absolute_path = get_path(context, request)

    # MODIFY
    IOperationFactory(FileSystemResource(
        relative_path)).modify()


    transaction.commit()
    return JSONResponse({})

def remove_view(context, request):
    """ remove view

    Remove a file from the index.  The path of the file is taken from the
    request.  The path is assumed to be *relative* to the file pool.

    @context    This is a ``RoutesContext`` instance
    @request    A webob request object
    """
    relative_path, absolute_path = get_path(context, request, _raise=False)

    # REMOVE
    IOperationFactory(FileSystemResource(
        relative_path)).remove()

    transaction.commit()
    return JSONResponse({})

def query_view(context, request):
    """ query view

    This view is called for queries.  The query is constructed from the
    request, a search using xapian is done and the results are sent back to the
    caller in JSON format.

    @context    This is a ``RoutesContext`` instance
    @request    A webob request object

    The result is a JSON encoded list of dicts as in::

        [{
            "url":      "http://localhost:1234/static/fashion.jpg"
            "mimetype": "image/jpg",
            "metadata": {
                "creation_date": "2008-10-02 17:43",
                "keywords": ["new york", "fashion"],
                ...
            },
        }, ... ]
    """
    start = 0
    limit = 100

    try:
        limit = int(request.params.get("limit"))
    except (TypeError, ValueError), e:
        pass
    try:
        start = int(request.params.get("start"))
    except (TypeError, ValueError), e:
        pass

    # construct query
    search_result = search(request.params.get("query"), start, limit)

    # format results
    data = []
    matches_estimated = search_result.matches_estimated
    resolver = component.getUtility(IResolver)
    for brain in search_result:
        resource = resolver.resolve(brain.id)
        rel_path = resource.path[len(resolver.path)+1:]
        data.append(
                dict(
                    url=os.path.join(context.host, rel_path),
                    mimetype=resource.mimetype,
                    metadata=brain.data,
                    )
                )

    return JSONResponse((matches_estimated, data))

def purge_view(context, request):
    raise NotImplementedError("Purge not yet implemented.")
