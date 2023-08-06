
The request object
====================

.. testsetup:: *
        
        from pesto.request import Request
        from pesto.testing import make_environ, TestApp

The ``request`` object gives access to all WSGI environment properties,
including request headers and server variables, as well as 
submitted form data. 

Core WSGI environment variables and other useful information is exposed as
attributes::

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

The API documentation at the end of this page contains the complete list of request attributes.

MultiDicts
----------

Many items of data accessible through the request object are exposed as
instances of ``pesto.utils.MultiDict``. This has a dictionary-like interface,
with additional methods for retrieving data where a key has multiple values
associated with it. For example:

.. doctest::

        >>> from pesto.testing import TestApp, make_environ
        >>> from pesto.request import Request
        >>> request = Request(make_environ(QUERY_STRING='a=Trinidad;b=Mexico;b=Honolulu'))
        >>> request.form.get('a')
        u'Trinidad'
        >>> request.form.get('b')
        u'Mexico'
        >>> request.form.getlist('b')
        [u'Mexico', u'Honolulu']

Form data
-----------

Form values are accessible from ``request.form``, a ``pesto.utils.MultiDict``
object, giving dictionary like access to submitted form data::

    request.form["email"]
    request.form.get("email")

As this is a very common usage, shortcuts exist::

    request["email"]
    request.get("email")

For GET requests, ``request.form`` contains data parsed from the URL query string. 
For POST requests, ``request.form`` contains only POSTED data. If a query
string was present in a POST request, it is necessary to use ``request.query``
to access this, which has the same interface.

Cookie data
------------

Cookies are accessible from the ``request.cookies`` MultiDict. See :doc:`cookies` for more information.

File uploads
-------------

The ``request.files`` dictionary has the same interface as ``request.form``,
but values are ``FileUpload`` objects, which allow you to access information
about uploaded files as well as the raw data::

    >>> from pesto.testing import TestApp
    >>> request = MockWSGI.make_post_multipart(
    ...    files=[('fileupload', 'uploaded.txt', 'text/plain', 'Here is a nice file upload for you')]
    ... ).request
    >>>
    >>> upload = request.files['fileupload']
    >>> upload.filename
    'uploaded.txt'
    >>> upload.file # doctest: +ELLIPSIS
    <cStringIO.StringO object at ...>
    >>> upload.headers # doctest: +ELLIPSIS
    <pesto.httputils.HTTPMessage instance at ...>
    >>> upload.headers['Content-Type']
    'text/plain'
    >>> upload.file.read()
    'Here is a nice file upload for you'

Maximum size limit
------------------

Posted data, including file uploads, is limited in size. This limit can be
altered by adjusting ``pesto.request.Request.MAX_SIZE`` and
``pesto.request.Request.MAX_MULTIPART_SIZE``.

Example 1 – set the global maximum size for POSTed data to 100kb:

.. doctest::

        >>> from pesto.request import Request
        >>> kb = 1024
        >>> Request.MAX_SIZE = 100 * kb

Example 2 – set the global maximum size for multipart/form-data POSTs to 4Mb.

The total data uploaded, including all file-uploads will be limited to 4Mb. Non
file-upload fields will be individually limited to 100Kb by the ``MAX_SIZE``
set in the previous example:

.. doctest::

        >>> Mb = 1024 * kb
        >>> Request.MAX_MULTIPART_SIZE = 4 * Mb

Pesto also supports overriding these limits on a per-request basis:

.. doctest::

        >>> def big_file_upload(request):
        ...     request.MAX_MULTIPART_SIZE = 100 * Mb
        ...     request.files['bigfile'].save('/tmp/bigfile.bin')
        ...     return Response(["Thanks for uploading a big file"])
        ...


Request module API documention
-------------------------------

.. automodule:: pesto.request
        :members:

