# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__all__ = ['currentrequest', 'to_wsgi', 'response']

import sys

from itertools import chain, takewhile

from pesto import response
from pesto.request import currentrequest, Request


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

        >>> import pesto.wsgiutils
        >>> from pesto.response import Response
        >>> 
        >>> def handler(request):
        ...     return Response([u"Whoa nelly!"])
        ...
        >>> wsgiapp = to_wsgi(handler)
        >>> print pesto.wsgiutils.MockWSGI().run(wsgiapp).headers
        [('Content-Type', 'text/html; charset=UTF-8')]
        >>> print pesto.wsgiutils.MockWSGI().run(wsgiapp).raw_response
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Whoa nelly!

    A more advanced example::

        >>> import pesto.wsgiutils
        >>> import pesto.dispatch
        >>> from pesto.response import Response
        >>>
        >>> d = pesto.dispatch.urldispatcher()
        >>>
        >>> @d.match('/home/<pagename:unicode>', "GET")
        ... def pagehandler(request, pagename):
        ...     return Response(["This page is %s" % pagename])
        >>>
        >>> @d.match('/anotherpage/<pagename:unicode>', "GET")
        ... def anotherpage(request, pagename):
        ...     return Response(["This is another page %s" % pagename])
        >>>
        >>> # Use pesto.wsgiutils.MockWSGI to check it all works
        >>> pesto.wsgiutils.MockWSGI('/home/amazing').run(d).output
        ['This page is amazing']
        >>> pesto.wsgiutils.MockWSGI('/anotherpage/of%20wonder').run(d).output
        ['This is another page of wonder']
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
            response = self._pesto_app(self.request, *self._app_args, **self._app_kwargs)
            self._content_iter = response(self.environ, self.start_response)
        return self._content_iter.next()

    def close(self):
        if self._content_iter is None:
            return
        response_close = getattr(self._content_iter, 'close', None)
        if response_close is not None:
            return response_close()

