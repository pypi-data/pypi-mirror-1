
The response object
=====================

The response object allows you to set headers and provides shortcuts for common
handler responses, such as redirection.

Constructing response objects
```````````````````````````````

At the minimum a ``Response`` needs the response content. If this is all you
specify, a successful response of type ``text/html`` will be generated.

    >>> from pesto.response import Response
    >>> Response(['<html><body><h1>Hello World</body></html>']) # doctest: +ELLIPSIS
    <pesto.response.Response object at ...>

The content must be an iterable object. For small applications a list is
convenient, but this object could be any python iterator.

HTTP headers and a status code can also be supplied. Here's a longer example, showing everything::

    >>> from pesto.response import Response
    >>> Response(
    ...     status = 405, # method not allowed
    ...     content_type = 'text/html',
    ...     allow = ['GET', 'POST'],
    ...     content = ['<html><body>Sorry, that method is not allowed</body></html>']
    ... ) # doctest: +ELLIPSIS
    <pesto.response.Response object at ...>

Headers can be supplied as a list of tuples (the same way the WSGI
``start_response`` function expects them), or as keyword arguments, or a mixture of the two::

    >>> Response(
    ...     status = 405, # method not allowed
    ...     headers = [ ('Content-Type', 'text/html'), ('Allow', 'GET'), ('Allow', 'POST') ],
    ...     content = ['<html><body>Sorry, that method is not allowed</body></html>']
    ... ) # doctest: +ELLIPSIS
    <pesto.response.Response object at ...>

    >>> Response(
    ...     status=405, # method not allowed
    ...     content_type='text/html',
    ...     allow=['GET', 'POST'],
    ...     content = ['<html><body>Sorry, that method is not allowed</body></html>']
    ... ) # doctest: +ELLIPSIS
    <pesto.response.Response object at ...>


Changing response objects
```````````````````````````

Response objects have a range of methods allowing you to add, remove and replace the headers and content. This makes it easy to chain handler functions together, each operating on the output of the last::

    >>> def handler1(request):
    ...     return Response(["Ten green bottles, hanging on the wall"], content_type='text/plain')
    ...
    >>> def handler2(request):
    ...     response = handler1(request)
    ...     return response.replace(content=[chunk.replace('Ten', 'Nine') for chunk in response.content])
    ...
    >>> def handler3(request):
    ...     response = handler2(request)
    ...     return response.replace(content_type='text/html')
    ...
    >>> from pesto.wsgiutils import MockWSGI
    >>> request = MockWSGI().request
    >>> handler1(request).content
    ['Ten green bottles, hanging on the wall']
    >>> handler1(request).headers
    [('Content-Type', 'text/plain')]
    >>>
    >>> handler2(request).content
    ['Nine green bottles, hanging on the wall']
    >>> handler2(request).headers
    [('Content-Type', 'text/plain')]
    >>>
    >>> handler3(request).content
    ['Nine green bottles, hanging on the wall']
    >>> handler3(request).headers
    [('Content-Type', 'text/html')]


Headers may be added, either singly::

    >>> r = Response(content = ['Whoa nelly!'])
    >>> r.headers
    [('Content-Type', 'text/html; charset=UTF-8')]
    >>> r = r.add_header('Cache-Control', 'private')
    >>> r.headers
    [('Content-Type', 'text/html; charset=UTF-8'), ('Cache-Control', 'private')]

or in groups::

    >>> r = Response(content = ['Whoa nelly!'])
    >>> r.headers
    [('Content-Type', 'text/html; charset=UTF-8')]
    >>> r = r.add_headers([('Content-Length', '11'), ('Cache-Control', 'Private')])
    >>> r.headers
    [('Content-Type', 'text/html; charset=UTF-8'), ('Content-Length', '11'), ('Cache-Control', 'Private')]
    >>> r = r.add_headers(x_powered_by='pesto')
    >>> r.headers
    [('Content-Type', 'text/html; charset=UTF-8'), ('Content-Length', '11'), ('Cache-Control', 'Private'), ('X-Powered-By', 'pesto')]

Removing and replacing headers is the same. See the API documentation for `pesto.response.Response` for details.

Integrating with WSGI
------------------------

It's often useful to be able to switch between the pesto library functions and
raw WSGI – for example, when writing WSGI middleware.

To aid this, ``Response`` objects are fully compliant WSGI applications::

    >>> def mywsgi_app(environ, start_response):
    ...     r = Response(content = ['Whoa nelly!'])
    ...     return r(environ, start_response)
    ...
    >>> MockWSGI().run(mywsgi_app).raw_response
    '200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nWhoa nelly!'

Secondly, it is possible to proxy a WSGI application through a response object,
capturing its output to allow further inspection and modification::

    >>> def wsgi_app1(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/plain')])
    ...     return [ "<html>"
    ...          "<body>"
    ...          "<h1>Hello World!</h1>"
    ...          "</body>"
    ...          "</html>"
    ...     ]
    ...
    >>> def wsgi_app2(environ, start_response):
    ...     response = Response.from_wsgi(wsgi_app1, environ, start_response)
    ...     return response.add_headers(x_powered_by='pesto')(environ, start_response)
    ...
    >>> MockWSGI().run(wsgi_app2).raw_response
    '200 OK\r\nContent-Type: text/plain\r\nX-Powered-By: pesto\r\n\r\n<html><body><h1>Hello World!</h1></body></html>'




Common responses
-----------------

Many canned error responses are available as ``Response`` classmethods::

    >>> from pesto.response import Response
    >>> def handler(request):
    ...     if not somecondition():
    ...         return Response.not_found()
    ...     return Response(['ok'])
    ...

    >>> def handler2(request):
    ...     if not somecondition():
    ...         return Response.forbidden()
    ...     return Response(['ok'])
    ...

Redirect responses
````````````````````

A temporary or permanent redirect may be achieved by returning ``pesto.response.Response.redirect()``. For example::

    >>> from pesto.response import *
    >>>
    >>> def redirect(request):
    ...     return Response.redirect("http://www.example.com")
    ...

Response module API documention
-------------------------------

.. automodule:: pesto.response
        :members:


