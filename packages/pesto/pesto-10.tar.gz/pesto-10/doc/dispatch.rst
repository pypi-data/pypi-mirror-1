
URL dispatch
==============

Pesto's ``urldispatcher`` objects help map URIs to handler functions. For
example::

    >>> from pesto import urldispatcher, Response
    >>> dispatcher = urldispatcher()

    >>> @dispatcher.match('/recipes', 'GET')
    ... def recipe_index(request):
    ...     return Response(['This is the recipe index page'])
    ...
    >>> @dispatcher.match('/recipes/<category:unicode>', 'GET')
    ... def recipe_index(request, category):
    ...     return Response(['This is the page for ', category, ' recipes'])
    ...

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
URL could handle the submission::

    @dispatcher.match('/contact-form', 'GET')
    def contact_form(request):
        """
        Display a contact form
        """

    @dispatcher.match('/contact-form', 'POST'):
    def contact_form_submit(request)
        """
        Process the form, eg by sending an email
        """

Dispatchers do not have to be function decorators. The following code is
equivalent to the previous example::

    dispatcher.match('/contact-form', GET=contact_form, POST=contact_form_submit)

Matching is always based on the path part of the URL (taken from the WSGI
``environ['PATH_INFO']`` value).

URI redirecting
---------------

A combination of the Response object and dispatchers can be used for URI
rewriting and redirection::

        >>> from pesto.wsgiutils import MockWSGI
        >>> from pesto import urldispatcher, Response
        >>> from pesto import response
        >>>
        >>> from functools import partial
        >>>
        >>> dispatcher = urldispatcher()
        >>> dispatcher.match('/old-link', GET=partial(Response.redirect, '/new-link', status=response.STATUS_MOVED_PERMANENTLY))
        >>> MockWSGI('/old-link').run(dispatcher).raw_response  # doctest: +ELLIPSIS
        "301 Moved Permanently..."



URI generation
---------------

Functions mapped by the dispatcher object are assigned a ``url`` method, allowing
URIs to be composed::

    >>> from pesto import urldispatcher, Response
    >>> dispatcher = urldispatcher()
    >>> @dispatcher.match('/recipes', 'GET')
    ... def recipe_index(request):
    ...     return Response(['this is the recipe index page'])
    ...
    >>> @dispatcher.match('/recipes/<recipe_id:int>', 'GET')
    ... def show_recipe(request, recipe_id):
    ...     return Response(['this is the recipe detail page for recipe #%d' % recipe_id])
    ...
    >>> from pesto.wsgiutils import MockWSGI
    >>> request = MockWSGI('http://example.com/').request
    >>> recipe_index.url(request=request)
    'http://example.com/recipes'
    >>> show_recipe.url(request=request, recipe_id=42)
    'http://example.com/recipes/42'

Dispatch module API documentation
----------------------------------

.. automodule:: pesto.dispatch
        :members:
