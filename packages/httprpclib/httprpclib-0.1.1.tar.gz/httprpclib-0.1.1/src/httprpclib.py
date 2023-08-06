"""
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
"""
from __future__ import with_statement
import contextlib as _contextlib
import functools as _functools
import httplib as _httplib
import sys as _sys
import urlparse as _urlparse


__author__ = 'Zachary Hirsch'
__author_email__ = 'zhirsch@umich.edu'
__version__ = '0.1.1'


class ServerProxy(object):
    """
    Implements a proxy that executes RESTful function calls over HTTP.
    """
    def __init__(self, base_url, config_file):
        self.base_url = _urlparse.urlparse(base_url)
        if self.base_url.scheme != 'http':
            raise ValueError("Only the 'http' scheme is supported")

        # Process the config file.
        self._context = {}
        execfile(config_file, self._context)

    def __getattr__(self, name):
        if name not in self._context:
            raise AttributeError("No HTTP-RPC method named '%s'" % name)
        return _Method(self, self._context[name])

    def _request(self, method, url, payload, allowed_status_codes,
                 allowed_content_types):
        """
        Perform an HTTP request and return the response.  Raise an HttpError if
        there's a problem communicating with the remote server.

        The response is a tuple of (status_code, fcontent).  The fcontent is a
        file-like object of the server's response.  It implements the read and
        close methods.
        """
        try:
            conn = _httplib.HTTPConnection(self.base_url.netloc, strict=True)
            url = _urlparse.urljoin(self.base_url.path, url)
            conn.request(method, url, payload)
            response = conn.getresponse()
        except HTTPException, exc:
            raise HttpError(str(exc))

        if (allowed_status_codes is not None and
            response.status not in allowed_status_codes):
            raise HttpError("Unexpected status code: %s" % response.status)

        content_type = response.getheader('Content-Type')
        if (allowed_content_types is not None and
            content_type not in allowed_content_types):
            raise HttpError("Unexpected content-type: %s" % content_type)

        return response.status, response


class HttpError(Exception):
    pass


class _Method(object):
    """
    Wrapper around a callable defined in the configuration file.  When called,
    acts as a coroutine with the wrapped function to perform an HTTP-RPC
    function call.
    """
    def __init__(self, owner, impl):
        self._owner = owner
        self._impl = impl

    def __call__(self, *args, **kwargs):
        with _contextlib.closing(self._impl(*args, **kwargs)) as gen:
            payload = gen.next()
            try:
                status_code, response = self._owner._request(
                    self._impl.method,
                    self._impl.url,
                    payload,
                    getattr(self._impl, 'status_codes', None),
                    getattr(self._impl, 'content_types', None),
                )
            except Exception:
                return gen.throw(*_sys.exc_info())
            with _contextlib.closing(response):
                return gen.send((status_code, response))


def method(method, url):
    """
    Decorator to mark a function as an HTTP-RPC method.  Adds some metadata to
    a function that is needed by the :class:`ServerProxy` class.
    """
    def decorator(func):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.method = method
        wrapper.url = url
        return wrapper
    return decorator


def expects(status_codes, content_types):
    """
    Decorator to declare which status codes and content types an HTTP-RPC
    method expects.
    """
    def decorator(func):
        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.status_codes = status_codes
        wrapper.content_types = content_types
        return wrapper
    return decorator
