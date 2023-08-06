# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__all__ = ['currentrequest', 'to_wsgi', 'response']

import sys

from itertools import chain, takewhile

from pesto import response
from pesto.request import currentrequest, Request
from pesto.httputils import RequestParseError


def to_wsgi(pesto_app):
    """
    A convenience function, equivalent to calling
    ``PestoWSGIApplication(pesto_app)`` directly.
    """
    return PestoWSGIApplication(pesto_app)

class PestoWSGIApplication(object):
    """
    A WSGI application wrapper around a Pesto handler function.

    The handler function should have the following signature:

        pesto_app(request) -> pesto.response.Response

    Synopsis::

        >>> from pesto.testing import TestApp
        >>> from pesto.response import Response
        >>> 
        >>> def handler(request):
        ...     return Response([u"Whoa nelly!"])
        ...
        >>> wsgiapp = PestoWSGIApplication(handler)
        >>> print TestApp(wsgiapp).get().headers
        [('Content-Type', 'text/html; charset=UTF-8')]
        >>> print TestApp(wsgiapp).get()
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Whoa nelly!
    """

    def __init__(self, pesto_app, *app_args, **app_kwargs):
        self._pesto_app = pesto_app
        self._app_args = app_args
        self._app_kwargs = app_kwargs
        self._content_iter = None
        self.environ = None
        self.start_response = None
        self.request = None

    def __call__(self, environ, start_response):
        self._content_iter = None
        self.environ = environ
        self.start_response = start_response
        self.request = Request(environ)
        return self

    def __iter__(self):
        return self

    def next(self):
        if self._content_iter is None:
            try:
                response = self._pesto_app(self.request, *self._app_args, **self._app_kwargs)
                self._content_iter = response(self.environ, self.start_response)
            except RequestParseError, e:
                response_close = getattr(self._content_iter, 'close', None)
                if response_close is not None:
                    response_close()
                self._content_iter = e.response()(self.environ, self.start_response)
        return self._content_iter.next()

    def close(self):
        if self._content_iter is None:
            return
        response_close = getattr(self._content_iter, 'close', None)
        if response_close is not None:
            return response_close()

