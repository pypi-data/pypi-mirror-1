
The response object
=====================

.. testsetup:: *

        from pesto.response import Response
        from pesto.testing import TestApp, make_environ
        from pesto import to_wsgi

The response object allows you to set headers and provides shortcuts for common
handler responses, such as redirection.

Constructing response objects
```````````````````````````````

At the minimum the ``pesto.response.Response`` constructor needs the response
content. If this is all you specify, a successful response of type
``text/html`` will be generated with your specified content.

.. testcode::

        def app(request):
                return Response(['<html><body><h1>Hello World</body></html>'])

.. testcode::
        :hide:

        print TestApp(to_wsgi(app)).get().text()

This will output:

.. testoutput::

        200 OK
        Content-Type: text/html; charset=UTF-8

        <html><body><h1>Hello World</body></html>

The content argument must be an iterable object – eg a list, a generator
expression or any python object that implements the iteration interface)

HTTP headers and a status code can also be supplied. Here's a longer example,
showing more options:

.. testcode::

        from pesto.response import Response

        def app(request):
                return Response(
                        status=405, # method not allowed
                        content_type='text/html',
                        allow=['GET', 'POST'],
                        content=['<html><body>Sorry, that method is not allowed</body></html>']
                )

.. testcode::
        :hide:

        print TestApp(to_wsgi(app)).get().text()

This will output:

.. testoutput::

        405 Method Not Allowed
        Allow: GET
        Allow: POST
        Content-Type: text/html

        <html><body>Sorry, that method is not allowed</body></html>

Headers can be supplied as a list of tuples (the same way the WSGI
``start_response`` function expects them), or as keyword arguments, or any
mixture of the two:

.. testcode::

        Response(
                ['<html><body>Sorry, that method is not allowed</body></html>'],
                status=405,
                headers=[('Content-Type', 'text/html'), ('Allow', 'GET'), ('Allow', 'POST')],
        )

        Response(
                ['<html><body>Sorry, that method is not allowed</body></html>'],
                status=405,
                content_type='text/html',
                allow=['GET', 'POST'],
        )


Changing response objects
```````````````````````````

Response objects have a range of methods allowing you to add, remove and
replace the headers and content. This makes it easy to chain handler functions
together, each operating on the output of the last:

.. testcode::

        def handler1(request):
                return Response(["Ten green bottles, hanging on the wall"], content_type='text/plain')
        
        def handler2(request):
                response = handler1(request)
                return response.replace(content=[chunk.replace('Ten', 'Nine') for chunk in response.content])
        
        def handler3(request):
                response = handler2(request)
                return response.replace(content_type='text/html')
    
.. doctest::

        >>> from pesto.testing import TestApp
        >>> print TestApp(to_wsgi(handler1)).get('/').text()
        200 OK
        Content-Type: text/plain
        <BLANKLINE>
        Ten green bottles, hanging on the wall

        >>> print TestApp(to_wsgi(handler2)).get('/').text()
        200 OK
        Content-Type: text/plain
        <BLANKLINE>
        Nine green bottles, hanging on the wall

        >>> print TestApp(to_wsgi(handler3)).get('/').text()
        200 OK
        Content-Type: text/html
        <BLANKLINE>
        Nine green bottles, hanging on the wall

Headers may be added, either singly:

.. doctest::

        >>> r = Response(content = ['Whoa nelly!'])
        >>> r.headers
        [('Content-Type', 'text/html; charset=UTF-8')]
        >>> r = r.add_header('Cache-Control', 'private')
        >>> r.headers
        [('Cache-Control', 'private'), ('Content-Type', 'text/html; charset=UTF-8')]

or in groups:

.. doctest::

        >>> r = Response(content = ['Whoa nelly!'])
        >>> r.headers
        [('Content-Type', 'text/html; charset=UTF-8')]
        >>> r = r.add_headers([('Content-Length', '11'), ('Cache-Control', 'Private')])
        >>> r.headers
        [('Cache-Control', 'Private'), ('Content-Length', '11'), ('Content-Type', 'text/html; charset=UTF-8')]
        >>> r = r.add_headers(x_powered_by='pesto')
        >>> r.headers
        [('Cache-Control', 'Private'), ('Content-Length', '11'), ('Content-Type', 'text/html; charset=UTF-8'), ('X-Powered-By', 'pesto')]

Removing and replacing headers is the same. See the API documentation for `pesto.response.Response` for details.

Integrating with WSGI
------------------------

It's often useful to be able to switch between Pesto handler functions and
WSGI application functions – for example, when writing WSGI middleware.

To aid this, ``Response`` objects are fully compliant WSGI applications::

        >>> def mywsgi_app(environ, start_response):
        ...     r = Response(content = ['Whoa nelly!'])
        ...     return r(environ, start_response)
        ...
        >>> print TestApp(mywsgi_app).get('/').text()
        200 OK
        Content-Type: text/html; charset=UTF-8
        <BLANKLINE>
        Whoa nelly!

Secondly, it is possible to proxy a WSGI application through a response object,
capturing its output to allow further inspection and modification::

        >>> def basic_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/html')])
        ...     return [ "<html>"
        ...          "<body>"
        ...          "<h1>Hello World!</h1>"
        ...          "</body>"
        ...          "</html>"
        ...     ]
        ...
        >>> def altered_wsgi_app(environ, start_response):
        ...     response = Response.from_wsgi(wsgi_app1, environ, start_response)
        ...     return response.add_headers(x_powered_by='pesto')(environ, start_response)
        ...
        >>> print TestApp(altered_wsgi_app).get('/').text()
        200 OK
        Content-Type: text/html
        X-Powered-By: pesto
        <BLANKLINE>
        <html><body><h1>Hello World!</h1></body></html>


Common responses
-----------------

Many canned error responses are available as ``Response`` classmethods:

.. doctest::

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

A temporary or permanent redirect may be achieved by returning ``pesto.response.Response.redirect()``. For example:

.. doctest::

    >>> def redirect(request):
    ...     return Response.redirect("http://www.example.com/")
    ...

Response module API documention
-------------------------------

.. automodule:: pesto.response
        :members:


