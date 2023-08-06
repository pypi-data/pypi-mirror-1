
URL dispatch
==============

.. testsetup:: *

        from pesto import to_wsgi
        from pesto.response import Response
        from pesto.testing import TestApp

Pesto's ``dispatcher_app`` is a useful WSGI application that can map URIs to
handler functions. For example:

.. testcode::

        from pesto import dispatcher_app, Response
        dispatcher = dispatcher_app()

        @dispatcher.match('/recipes', 'GET')
        def recipe_index(request):
                return Response(['This is the recipe index page'])

        @dispatcher.match('/recipes/<category:unicode>', 'GET')
        def recipe_index(request, category):
                return Response(['This is the page for ', category, ' recipes'])

.. doctest::
        :hide:

        >>> TestApp(dispatcher).get("/recipes").body
        'This is the recipe index page'
        >>> TestApp(dispatcher).get("/recipes/goop").body
        'This is the page for goop recipes'

Dispatchers can use prefined patterns expressions to extract data from URIs and
pass it on to a handler. The following expression types are supported:


        * ``unicode`` - any unicode string (not including forward slashes)
        * ``path`` - any path (includes forward slashes)
        * ``int`` - any integer
        * ``any`` - a string matching a list of alternatives

It is also possible to add your own types so you to match custom patterns (see
the API documentation for ``ExtensiblePattern.register_pattern``). Match
patterns are delimited by angle brackets, and generally have the form
``<name:type>``. Some examples:


        * ``'/recipes/<category:unicode>/<id:int>'``. This would match a
          URI such as ``/recipes/fish/7``, and call the handler function with
          the arguments ``category=u'fish', id=7``.

        * ``'/entries/<year:int>/<month:int>``. This would match a URI
          such as ``/entries/2008/05``, and call the handler function with the
          arguments ``year=2008, month=5``. 

        * ``'/documents/<directory:path>/<name:unicode>.pdf``. This would
          match a URI such as ``/documents/all/2008/topsecret.pdf``, and call the handler function with
          the arguments ``directory=u'all/2008/', name=u'topsecret'``.


You can also map separate handlers to different HTTP methods for the same URL,
eg the ``GET`` method could display a form, and the ``POST`` method of the same
URL could handle the submission:

.. testcode::

    @dispatcher.match('/contact-form', 'GET')
    def contact_form(request):
        """
        Display a contact form
        """

    @dispatcher.match('/contact-form', 'POST')
    def contact_form_submit(request):
        """
        Process the form, eg by sending an email
        """

Dispatchers do not have to be function decorators. The following code is
equivalent to the previous example:

.. testcode::

    dispatcher.match('/contact-form', GET=contact_form, POST=contact_form_submit)

Matching is always based on the path part of the URL (taken from the WSGI
``environ['PATH_INFO']`` value).

URI redirecting
---------------

A combination of the Response object and dispatchers can be used for URI
rewriting and redirection:

.. testcode::

        from functools import partial

        from pesto import dispatcher_app, Response
        from pesto import response

        dispatcher = dispatcher_app()
        dispatcher.match('/old-link', GET=partial(Response.redirect, '/new-link', status=response.STATUS_MOVED_PERMANENTLY))

Any calls to ``/old-link`` will now be met with:

.. testcode::
        :hide:

        print TestApp(dispatcher).get('/old-link').text()

.. testoutput::

        301 Moved Permanently
        Content-Type: text/html; charset=UTF-8
        Location: http://localhost/new-link
        ...


URI generation
---------------

Functions mapped by the dispatcher object are assigned a ``url`` method, allowing
URIs to be generated:

.. testcode::

        from pesto import dispatcher_app, Response

        dispatcher = dispatcher_app()
        @dispatcher.match('/recipes', 'GET')
        def recipe_index(request):
                return Response(['this is the recipe index page'])

        @dispatcher.match('/recipes/<recipe_id:int>', 'GET')
        def show_recipe(request, recipe_id):
                return Response(['this is the recipe detail page for recipe #%d' % recipe_id])

Calling the ``url`` method will generate fully qualified URLs for any function
mapped by a dispatcher:

.. doctest::

        >>> from pesto.testing import make_environ
        >>> from pesto.request import Request
        >>> request = Request(make_environ(SERVER_NAME='example.com'))
        >>>
        >>> recipe_index.url()
        'http://example.com/recipes'
        >>> show_recipe.url(recipe_id=42)
        'http://example.com/recipes/42'

Note: the ``url`` method needs a live request object, usually acquired through
``pesto.currentrequest``, although it can also be passed as a parameter.
If you need to call this method outside of a WSGI request context then you will
need to simulate a WSGI environ to generate a Request object.

Repurposing handler functions
-----------------------------

Suppose you have a function that returns a list of orders, with the price and
date, and you want to this list both as regular HTML page and in JSON notation
for AJAX enhancement. Instead of writing two handlers – one for the HTML
response and one for the JSON – it's possible to use the same handler function
to serve both types of request.

We'll start by creating some sample data:

.. testcode::

        from datetime import date

        class Order(object):

            def __init__(self, price, date):
                    self.price = price
                    self.date = date

        orders = [
            Order(12.99, date(2009, 7, 1)),
            Order(7.75, date(2009, 8, 1)),
            Order(8.25, date(2009, 8, 1)),
        ]

The handler function is going to return a Python data structure, and we'll add
decorator functions that can convert this data structure to JSON and HTML:

.. testcode::

        import json
        from cgi import escape
        from functools import wraps

        def to_json(func):
            """
            Wrap a Pesto handler to return a JSON-encoded string from a python
            data structure.
            """

            @wraps(func)
            def to_json(request, *args, **kwargs):
                result = func(request, *args, **kwargs)
                if isinstance(result, Response):
                    return result
                return Response(
                    content=[json.dumps(result)],
                    content_type='application/json'
                )
            return to_json

        def to_html(func):
            def to_html(request, *args, **kwargs):

                data = func(request, *args, **kwargs)
                if not data:
                        return Response([], content_type='text/html')

                keys = sorted(data[0].keys())
                result = ['<table>\n']
                result.append('<tr>\n')
                result.extend('  <th>%s</th>\n' % escape(key) for key in keys)
                result.append('</tr>\n')
                for item in data:
                        result.append('<tr>\n')
                        result.extend('  <td>%s</td>\n' % escape(str(item[key])) for key in keys)
                        result.append('</tr>\n')
                result.append('</table>')
                return Response(result)
            return to_html

(Note that for a real world application you should use a templating system rather than
putting HTML directly in your code. But for this small example it's fine).

Now we can write a handler function to serve the data. ``dispatcher_app.match``
has a ``decorators`` argument that allows us to use the same function to
serve both the HTML and JSON versions by wrapping it in different decorators
for each:

.. testcode::

        from pesto import dispatcher_app
        dispatcher = dispatcher_app()
        @dispatcher.match('/orders.json', 'GET', decorators=[to_json])
        @dispatcher.match('/orders.html', 'GET', decorators=[to_html])
        def list_orders(request):
            return [
                    {
                            'date': order.date.strftime('%Y-%m-%d'),
                            'price': order.price,
                    } for order in orders
            ]


We can now call this function in three ways. First, the HTML version:

.. doctest::

        >>> from pesto.testing import TestApp
        >>> print TestApp(dispatcher).get('/orders.html').body
        <table>
        <tr>
          <th>date</th>
          <th>price</th>
        </tr>
        <tr>
          <td>2009-07-01</td>
          <td>12.99</td>
        </tr>
        <tr>
          <td>2009-08-01</td>
          <td>7.75</td>
        </tr>
        <tr>
          <td>2009-08-01</td>
          <td>8.25</td>
        </tr>
        </table>

And the JSON version:

.. doctest::

        >>> print TestApp(dispatcher).get('/orders.json').body
        [{"date": "2009-07-01", "price": 12.99}, {"date": "2009-08-01", "price": 7.75}, {"date": "2009-08-01", "price": 8.25}]

Finally, we can call the function just as a regular python function. We need to
pass the function a (dummy) request object in this case::

        >>> from pprint import pprint
        >>> from pesto.testing import make_environ
        >>> dummy_request = make_environ()
        >>> pprint(list_orders(dummy_request))
        [{'date': '2009-07-01', 'price': 12.99},
         {'date': '2009-08-01', 'price': 7.75},
         {'date': '2009-08-01', 'price': 8.25}]


Dispatch module API documentation
----------------------------------

.. automodule:: pesto.dispatch
        :members:
