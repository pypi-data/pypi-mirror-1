
Cookies
=========

You can read cookies through the request object, and construct cookies using
the functions in ``pesto.cookies``. 

Reading a cookie
-----------------

The easiest way to read a single cookie is to query the ``request.cookie_dict``
attribute. This is a dictionary mapping cookie names to single instances of
``pesto.cookie.Cookie``::

    def handler(request):
        if request.cookie_dict.get('secret_code').value == 'marmot':
            return Response(['pass, friend'])
        else:
            raise Forbidden()

Reading multiple cookies with the same name::

    def handler(request):
        parts = [ cookie.value for cookie in request.cookies_by_name('partnumber') ]

Setting cookies
-----------------

Simply assign an instance of ``pesto.cookie.Cookie`` to a set-cookie header::

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

Clearing cookies
-----------------

To clear a cookie is to expire it. Set a new cookie with the same details as
the one you are clearing, but with no value and maxage=0::

    def handler(request):
        return Response(
            ['blah'],
            set_cookie=pesto.cookie.Cookie(
                name='partnumber',
                value='',
                path='/acme',
                maxage=0,
                domain='example.com'
            )
        )

Cookie module API documention
------------------------------

.. automodule:: pesto.cookie
        :members:
