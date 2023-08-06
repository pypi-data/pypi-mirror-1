httprpclib version 0.1

A library that eases the use of RESTful web services.

This functions similarly to the standard xmlrpclib module.  It creates a proxy
object that converts Python function calls to HTTP requests.  The difference is
that there's a user-defined shim between the function call and the HTTP
request.

These shims are implemented as corountines using the generator call/throw/close
API described in PEP 342.  Each shim must yield exactly twice.  The first yield
provides the body of the HTTP request (or None if there isn't a body) and is
returned the status code and a file-like object of the body of the response.
The second yield provides the return value of the original function call.

Here's an example of a shim:

    import json
    from httprpclib import expects, method

    @method('GET', 'api/json/repositories/')
    @expects([200], ['application/json'])
    def get_repositories():
        status_code, response = (yield)
        yield json.load(response)

Here's how the shim is use with this module:

    import httprpclib

    rpc = httprpclib.ServerProxy('http://demo.review-board.org',
                                 '../examples/reviewboard.cfg')
    print rpc.get_repositories()

Written by and copyright 2009 Zachary Hirsch <zhirsch@umich.edu>.
