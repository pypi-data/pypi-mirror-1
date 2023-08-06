
Cookies
=========

.. testsetup:: *

        from pesto.testing import TestApp
        from pesto import to_wsgi
        from pesto.response import Response
        import pesto.cookie

You can read cookies through the request object, and construct cookies using
the functions in ``pesto.cookies``. 

Reading a cookie
-----------------

The easiest way to read a single cookie is to query the ``request.cookies``
attribute. This is a ``pesto.utils.MultiDict`` mapping cookie names to single
instances of ``pesto.cookie.Cookie``:

.. testcode::

        def handler(request):
                secret = request.cookies.get('secret')
                if secret and secret.value == 'marmot':
                        return Response(['pass, friend'])
                else:
                        return Response.forbidden()

.. doctest::
        :hide:

        >>> app = TestApp(to_wsgi(handler))
        >>> app.get(HTTP_COOKIE='secret=marmot').body
        'pass, friend'
        >>> app.get(HTTP_COOKIE='secret=doormat').status
        '403 Forbidden'


Setting cookies
-----------------

Simply assign an instance of ``pesto.cookie.Cookie`` to a set-cookie header:

.. testcode::

    def handler(request):
        return Response(
            ['blah'],
            set_cookie=pesto.cookie.Cookie(
                name='partnumber',
                value='Rocket_Launcher_0001',
                path='/acme',
                maxage=3600,
                domain='example.com'
            )
        )

.. doctest::
        :hide:

        >>> app = TestApp(to_wsgi(handler))
        >>> print app.get().text()
        200 OK
        Content-Type: text/html; charset=UTF-8
        Set-Cookie: partnumber=Rocket_Launcher_0001;Max-Age=3600;Path=/acme;Domain=example.com;Version=1;Expires=...
        ...



Clearing cookies
-----------------

To expire a cookie is to clear it. Set a new cookie with the same details as
the one you are clearing, but with no value and maxage=0:

.. testcode::

    def handler(request):
        return Response(
            [],
            set_cookie=pesto.cookie.Cookie(
                name='partnumber',
                value='',
                path='/acme',
                maxage=0,
                domain='example.com'
            )
        )

.. doctest::
        :hide:

        >>> app = TestApp(to_wsgi(handler))
        >>> print app.get().text()
        200 OK
        Content-Type: text/html; charset=UTF-8
        Set-Cookie: partnumber=;Max-Age=0;Path=/acme;Domain=example.com;Version=1;Expires=...
        ...


Cookie module API documention
------------------------------

.. automodule:: pesto.cookie
        :members:
