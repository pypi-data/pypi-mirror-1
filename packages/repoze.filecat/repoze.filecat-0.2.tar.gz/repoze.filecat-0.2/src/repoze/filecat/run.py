from repoze.bfg import router
from repoze.bfg import security
from repoze import filecat

import xapian
import resolver

class RoutesContext(object):
    __acl__ = [
            (security.Allow, security.Everyone, 'view'),
            ]

    def __init__(self, controller, host, path):
        self.controller = controller
        self.path = path
        self.host = host

def make_app(global_config, path=None, host=None, database=None):
    def context_factory(controller, **kw):
        return RoutesContext(controller, host, path)

    # xapian indexer configuration
    xapian.xapian_config(path, database)

    # create application
    app = router.make_app(context_factory, filecat)

    # provide xapian connection utility
    app.registry.registerUtility(xapian.Connection(database))

    # register resolver
    app.registry.registerUtility(resolver.FileSystemResolver(path))

    return app

if __name__ == '__main__':
    from paste import httpserver
    app = make_app(None)
    httpserver.serve(app, host='0.0.0.0', port='5431')
    
