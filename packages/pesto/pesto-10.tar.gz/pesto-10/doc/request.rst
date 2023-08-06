
The request object
====================

The ``request`` object gives access to all server variables and submitted form
data. Form values are accessed in a dictionary like fashion::

    request.get("email")
    request["email"]

For more control over the submitted values, you can access ``request.form``, a
dictionary-style wrapper around python's `cgi.FieldStorage <http://docs.python.org/lib/cgi-intro.html>`_. This provides the usual dictionary access, for example::

    >>> from pesto.wsgiutils import MockWSGI
    >>> request = MockWSGI("http://example.com/?name=Fred;name=Ginger").request
    >>> submitted_items = request.form.keys()
    >>> request.form.getfirst("name")
    u'Fred'
    >>> request.form.getlist("name")
    [u'Fred', u'Ginger']

Note that the underlying ``cgi.FieldStorage`` objects may be accessed via
``request.getstorage``. This provides an easier way to access the lower-level
API offered by ``cgi``, useful for processing file uploads::

    >>> storage = request.getstorage('fileupload')
    >>> storage.filename #doctest: +SKIP
    'uploaded.txt'
    >>> storage.file #doctest: +SKIP
    <cStringIO.StringO object at ...>
    >>> storage.headers #doctest: +SKIP
    <rfc822.Message instance at ...>

Core WSGI environment variables and other useful information is exposed as attributes::

    >>> from pesto.request import Request
    >>> environ = {
    ...     'PATH_INFO': '/pages/index.html',
    ...     'SCRIPT_NAME': '/myapp',
    ...     'REQUEST_METHOD': 'GET',
    ...     'SERVER_PROTOCOL': 'http',
    ...     'SERVER_NAME': 'example.org',
    ...     'SERVER_PORT': '80'
    ... }
    >>> request = Request(environ)
    >>> request.script_name
    '/myapp'
    >>> request.path_info
    '/pages/index.html'
    >>> request.application_uri
    'http://example.org/myapp'

Have a look in the API documentation at the end of this page for the complete list of request attributes.


Request module API documention
-------------------------------

.. automodule:: pesto.request
        :members:

