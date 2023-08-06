# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

import cgi
import os
import posixpath
import re
import threading
from urllib import quote, quote_plus

from urlparse import urlunparse
try:
    from functools import partial
except ImportError:
    from pesto.utils import partial

import pesto.response
from pesto.cookie import parse_cookie_header, Cookie

__all__ = ['Request', 'currentrequest',]

DEFAULT_ENCODING = 'UTF-8'

# This object will contain a reference to the current request
try:
    __local__ = threading.local()
except AttributeError:
    import logging
    logging.warn("threading.local not available!")
    class mocklocal(object):
        request = None
    __local__ = mocklocal()

def currentrequest():
    """
    Return the current WSGIRequest object, or ``None`` if no request object is
    available.
    """
    try:
        return __local__.request
    except AttributeError:
        return None

class Request(object):
    """
    Models an HTTP request.
    """

    parse_content_type = re.compile(r'\s*(.*);\s*charset=([\w\d\-]+)\s*$')

    _session = None
    _form = None
    _files = None
    _query = None
    _cookies = None

    def __new__(cls, environ):
        u"""
        Ensure the same instance is returned when called multiple times on the
        same environ object.

        >>> from pesto.wsgiutils import MockWSGI
        >>> env1 = MockWSGI().environ
        >>> env2 = MockWSGI().environ
        >>> Request(env1) is Request(env1)
        True
        >>> Request(env2) is Request(env2)
        True
        >>> Request(env1) is Request(env2)
        False
        """
        try:
            return environ['pesto.request']
        except KeyError:
            request = object.__new__(cls)
            __local__.request = request
            request.environ = environ
            request.environ['pesto.request'] = request
            return request

    def form(self):
        """
        Return the contents of any submitted request.

        If the form has been submitted via POST, GET parameters are also
        available via ``WSGIRequest.query``.
        """
        if self._form is None:
            self._form = FieldStorageWrapper(
                cgi.FieldStorage(
                    fp=self.environ['wsgi.input'],
                    environ=self.environ
                ),
                self.decode
            )
        return self._form
    form = property(form)

    def files(self):
        """
        Return ``FileUpload`` objects for all uploaded files
        """
        form = self.form
        if self._files is None:
            from pesto.wsgiutils import MultiDict
            files = [(key, form.getstorage(key)) for key in form]
            files = MultiDict([(key, FileUpload(storage)) for key, storage in files if hasattr(storage, 'file')])
            self._files = files
        return self._files
    files = property(files)

    def query(self):
        """
        Return a ``FieldStorageWrapper`` for any querystring submitted data.

        This is available regardless of whether the original request was a
        ``GET`` request.

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> mock = MockWSGI("http://example/?animal=moose")
            >>> mock.request.query.get('animal')
            u'moose'

        Note that this property is unaffected by the presence of POST data::

            >>> from pesto.wsgiutils import MockWSGI
            >>> from StringIO import StringIO
            >>> postdata = 'animal=hippo'
            >>> mock = MockWSGI(
            ...     "http://example/?animal=moose",
            ...     REQUEST_METHOD="POST",
            ...     CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8",
            ...     CONTENT_LENGTH=len(postdata),
            ...     wsgi_input=StringIO(postdata)
            ... )
            >>> mock.request.form.get('animal')
            u'hippo'
            >>> mock.request.query.get('animal')
            u'moose'
        """
        if self._query is None:
            self._query = FieldStorageWrapper(
                cgi.FieldStorage(None, environ={'REQUEST_METHOD' : 'GET', 'QUERY_STRING' : self.environ.get('QUERY_STRING')}),
                self.decode
            )
        return self._query
    query = property(query)

    def __getitem__(self, key):
        """
        Return the value of key from submitted form values.
        """
        marker = []
        v = self.get(key, marker)
        if v is marker:
            raise KeyError(key)
        return v

    def get(self, key, default=None):
        """
        Looks up a key in submitted form values
        """
        return self.form.get(key, default)

    def getfirst(self, key, default=None):
        """
        Looks up a key in submitted form values
        """
        return self.form.getfirst(key, default)

    def getstorage(self, key, default=None):
        """
        Return the cgi.FieldStorage item corresponding to ``key``.

        See ``FieldStorageWrapper.getstorage`` for documentation.
        """
        return self.form.getstorage(key, default)

    def charset(self):
        try:
            match = self.parse_content_type.match(self.environ['CONTENT_TYPE'])
        except KeyError:
            return DEFAULT_ENCODING
        else:
            if match:
                return match.group(2)
        return DEFAULT_ENCODING
    charset = property(charset)


    def decode(self, s):
        """
        Decode a byte-string into unicode based on the content type presented
        by the client (if any), or against a predefined list of alternatives if
        not.

        If the Content-Type header is present, try to use any encoding
        specified there to decode the string.

        Otherwise the DEFAULT_ENCODING will be used, with errors suppressed.

        Most browsers will submit information in the same encoding as the form
        page was issued in. If you want to handle form data as UTF-8 (the
        default expected by this library) you should ensure your forms are sent
        to the browser as UTF-8 documents. This can be achieved by:

        1. Setting the ``Content-Type`` header appropriately. This should be set as follows::

            Content-Type: text/html; charset=UTF-8

        1. Adding a ``<meta>`` header to the form page::

            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>

        """
        try:
            match = self.parse_content_type.match(self.environ['CONTENT_TYPE'])
        except KeyError:
            pass
        else:
            if match:
                return s.decode(match.group(2), 'ignore')

        if type(s) == unicode:
            return s
        return s.decode(DEFAULT_ENCODING, 'ignore')

    def getlist(self, key):
        """
        Return a form value as a list.
        """
        return map(self.decode, self.form.getlist(key))

    def __contains__(self, key):
        return self.form.has_key(key)

    def cookies(self):
        """
        Return a list of cookies read from the request headers.

        See rfc2109, section 4.4
        """
        if self._cookies is None:
            self._cookies = parse_cookie_header(self.get_header("Cookie"))
        return self._cookies
    cookies = property(
        cookies, None, None,
        cookies.__doc__
    )

    def cookies_by_name(self, name):
        """
        Return a list of cookies with the given name

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> mock = MockWSGI(
            ...     HTTP_COOKIE='''$Version="1";
            ...     Customer="WILE_E_COYOTE";
            ...     Part="Rocket_0001";
            ...     Part="Catapult_0032"
            ... ''')
            >>> [c.value for c in mock.request.cookies_by_name('Customer')]
            ['WILE_E_COYOTE']
            >>> [c.value for c in mock.request.cookies_by_name('Part')]
            ['Rocket_0001', 'Catapult_0032']

        """
        return [ cookie for cookie in self.cookies if cookie.name == name ]

    def cookie_by_name(self, name):
        """
        Returns a single named cookie. If the UA has sent multiple cookies
        with the same name, only the first will be returned.

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> mock = MockWSGI(
            ...     HTTP_COOKIE='''$Version="1";
            ...     Customer="WILE_E_COYOTE";
            ...     Part="Rocket_0001";
            ...     Part="Catapult_0032"
            ... ''')
            >>> mock.request.cookie_by_name('Customer').value
            'WILE_E_COYOTE'
            >>> mock.request.cookie_by_name('Part').value
            'Rocket_0001'
        """
        try:
            return self.cookies_by_name(name)[0]
        except IndexError:
            raise KeyError('Cookie %r not found' % (name,))

    def cookie_dict(self):
        """
        Return a dictionary of cookies mapped on cookie name
        """
        d = {}
        for item in self.cookies:
            d.setdefault(item.name, item)
        return d
    cookie_dict = property(cookie_dict)

    def get_header(self, name, default=None):
        """
        Return an arbitrary HTTP header from the request.

        name
            HTTP header name, eg 'User-Agent' or 'If-Modified-Since'.

        default
            default value to return if the header is not set.

        Technical note:

        Headers in the original HTTP request are always formatted like this::

            If-Modified-Since: Thu, 04 Jan 2007 21:41:08 GMT

        However, in the WSGI environ dictionary they appear as follows::

            {
                ...
                'HTTP_IF_MODIFIED_SINCE': 'Thu, 04 Jan 2007 21:41:08 GMT'
                ...
            }

        Despite this, this method expects the *former* formatting (with
        hyphens), and is not case sensitive.

        """
        return self.environ.get(
            'HTTP_' + name.upper().replace('-', '_'),
            default
        )

    def request_path(self):
        """
        Return the path component of the requested URI
        """
        scheme, netloc, path, params, query, frag = self.parsed_uri
        return path
    request_path = property(request_path, doc=request_path.__doc__)

    def request_uri(self):
        """
        Return the absolute URI, including query parameters.
        """
        return urlunparse(self.parsed_uri)
    request_uri = property(request_uri, doc=request_uri.__doc__)

    def application_uri(self):
        """
        Return the base URI of the WSGI application (ie the URI up to
        SCRIPT_NAME, but not including PATH_INFO or query information).

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> m = MockWSGI('https://example.com/animals/alligator.html', SCRIPT_NAME='/animals')
            >>> m.request.application_uri
            'https://example.com/animals'
        """
        uri = self.parsed_uri
        scheme, netloc, path, params, query, frag = self.parsed_uri
        return urlunparse((scheme, netloc, self.script_name, '', '', ''))
    application_uri = property(application_uri, doc=request_uri.__doc__)


    def parsed_uri(self):
        """
        Returns the current URI as a tuple of the form::

            (
             addressing scheme, network location, path,
             parameters, query, fragment identifier
            )

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> m = MockWSGI('https://example.com/animals/view?name=alligator')
            >>> m.request.parsed_uri
            ('https', 'example.com', '/animals/view', '', 'name=alligator', '')

        Note that the port number is stripped if the addressing scheme is
        'http' and the port is 80, or the scheme is https and the port is 443::

            >>> from pesto.wsgiutils import MockWSGI
            >>> m = MockWSGI('http://example.com:80/animals/view?name=alligator')
            >>> m.request.parsed_uri
            ('http', 'example.com', '/animals/view', '', 'name=alligator', '')
        """
        env = self.environ.get
        script_name = env("SCRIPT_NAME", "")
        path_info = env("PATH_INFO", "")
        query_string = env("QUERY_STRING", "")
        scheme = env('wsgi.url_scheme', 'http')

        try:
            host = self.environ['HTTP_HOST']
            if ':' in host:
                host, port = host.split(':', 1)
            else:
                port = self.environ['SERVER_PORT']
        except KeyError:
            host = self.environ['SERVER_NAME']
            port = self.environ['SERVER_PORT']

        if (scheme == 'http' and port == '80') \
            or (scheme == 'https' and port == '443'):
            netloc = host
        else:
            netloc = host + ':' + port

        return (
            scheme,
            netloc,
            script_name + path_info,
            '', # Params
            query_string,
            '', # Fragment
        )
    parsed_uri = property(parsed_uri, doc=parsed_uri.__doc__)

     # getters for environ properties
    def _get_env(self, name, default=None):
        """
        Return a value from the WSGI environment
        """
        return self.environ.get(name, default)

    env_prop = lambda name, doc, default=None, _get_env=_get_env: property(
        partial(_get_env, name=name, default=None), doc=doc
    )

    content_type  = env_prop('CONTENT_TYPE', "HTTP Content-Type header")
    document_root = env_prop('DOCUMENT_ROOT', "Server document root")
    path_info     = env_prop('PATH_INFO', "WSGI PATH_INFO value", '')
    query_string  = env_prop('QUERY_STRING', "WSGI QUERY_STRING value")
    script_name   = env_prop('SCRIPT_NAME', "WSGI SCRIPT_NAME value")
    server_name   = env_prop('SERVER_NAME', "WSGI SERVER_NAME value")
    remote_addr   = env_prop('REMOTE_ADDR', "WSGI REMOTE_ADDR value")

    def referrer(self):
        """
        Return the HTTP referrer header, or None if this is not available.
        """
        return self.get_header('Referer')
    referrer = property(referrer, doc=referrer.__doc__)

    def user_agent(self):
        """
        Return the HTTP user agent header, or None if this is not available.
        """
        return self.get_header('User-Agent')
    user_agent = property(user_agent, doc=user_agent.__doc__)

    def request_method(self):
        """
        Return the HTTP method used for the request, eg ``GET`` or ``POST``.
        """
        return self.environ.get("REQUEST_METHOD").upper()
    request_method = property(request_method, doc=request_method.__doc__)


    def session(self):
        """
        Return the session associated with this request.

        Requires a session object to have been inserted into the WSGI
        environment by a middleware application (see
        ``pesto.session.base.sessioning_middleware`` for an example).
        """
        return self.environ["pesto.session"]

    session = property(
        session, None, None,
        doc = session.__doc__
    )


    def make_uri(
        self, scheme=None, netloc=None,
        path=None, parameters=None,
        query=None, fragment=None,
        urlquote = True
    ):
        r"""
        Make a new URI based on the current URI, replacing any of the six
        elements:

            scheme, netloc, path, parameters, query, fragment

        Synopsis:

        Calling request.make_uri with no arguments will return the current URI::

            >>> from wsgiutils import MockWSGI
            >>> request = MockWSGI('http://example.com/foo').request
            >>> request.make_uri()
            'http://example.com/foo'

        Using keyword arguments it is possible to override any part of the URI::
            >>> request.make_uri(scheme='ftp')
            'ftp://example.com/foo'

            >>> request.make_uri(path='/bar')
            'http://example.com/bar'

            >>> request.make_uri(query={'page' : '2'})
            'http://example.com/foo?page=2'

        The path and query values are URL escaped before being returned::

            >>> request.make_uri(path=u'/caff\u00e8 latte')
            'http://example.com/caff%C3%A8%20latte'

        If a relative path is passed, the returned URI is joined to the old in
        the same way as a web browser would interpret a relative HREF in a
        document at the current location.

            >>> request = MockWSGI('http://example.com/banana/milkshake').request
            >>> request.make_uri(path='pie')
            'http://example.com/banana/pie'

            >>> request.make_uri(path='../strawberry')
            'http://example.com/strawberry'

            >>> request.make_uri(path='../../../plum')
            'http://example.com/plum'

            >>> request = MockWSGI('http://example.com/banana/milkshake/').request
            >>> request.make_uri(path='pie')
            'http://example.com/banana/milkshake/pie'

        Note that a URI with a trailing slash will have different behaviour
        from one without a trailing slash::

            >>> MockWSGI('http://example.com/banana/milkshake/').request.make_uri(path='mmmmm...')
            'http://example.com/banana/milkshake/mmmmm...'

            >>> MockWSGI('http://example.com/banana/milkshake').request.make_uri(path='mmmm....')
            'http://example.com/banana/mmmm....'

        """
        uri = []

        parsed_uri = self.parsed_uri

        if path is not None:
            if isinstance(path, unicode):
                path = path.encode(DEFAULT_ENCODING)
            if path[0] != '/':
                path = posixpath.join(posixpath.dirname(parsed_uri[2]), path)
                path = posixpath.normpath(path)
        else:
            path = parsed_uri[2]

        path = quote(path)

        if query is not None and isinstance(query, dict):
            from pesto.wsgiutils import make_query
            query = make_query(query)

        for specified, parsed in zip((scheme, netloc, path, parameters, query, fragment), parsed_uri):
            if specified is not None:
                uri.append(specified)
            else:
                uri.append(parsed)

        return urlunparse(uri)

    def text(self):
        """
        Return a useful text representation of the request
        """
        import pprint
        return "<%s\n\trequest_uri=%s\n\trequest_path=%s\n\t%s\n\t%s>" % (
                self.__class__.__name__,
                self.request_uri,
                self.request_path,
                pprint.pformat(self.environ),
                pprint.pformat(self.form.items()),
        )

class FieldStorageWrapper(object):
    """
    Thin wrapper around cgi.FieldStorage
    """

    def __init__(self, fs, decode_func):
        self._fs = fs
        self._override = {}
        self._decode_func = decode_func

    def __getitem__(self, key):
        marker = []
        v = self.getfirst(key, marker)
        if v is marker:
            raise KeyError(key)
        return v

    def __getattr__(self, attr):
        return self._decode_func(getattr(self._fs, attr))

    def __setitem__(self, key, value):
        self._override[key] = value

    def keys(self):
        """ dict keys method """
        return self._fs.keys() + [ k for k in self._override.keys() if k not in self._fs ]

    def __iter__(self):
        return iter(self.keys())

    def itemslist(self):
        """
        Like the ``items`` method, but returning a list of items for each key.

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> m = MockWSGI("http://example/?icecream=y;flavour=lemon;flavour=chocolate;")
            >>> sorted(m.request.form.itemslist())
            [('flavour', [u'lemon', u'chocolate']), ('icecream', [u'y'])]

        """
        return [ (k, self.getlist(k)) for k in self.keys() ]

    def items(self):
        """
        Dictionary items method

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> m = MockWSGI("http://example/?icecream=y;flavour=lemon;flavour=chocolate;")
            >>> sorted(m.request.form.items())
            [('flavour', u'lemon'), ('icecream', u'y')]
        """
        return [ (k, self.get(k)) for k in self.keys() ]

    def values(self):
        """ dict values method """
        return [ self.get(k) for k in self.keys() ]

    def getfirst_raw(self, key, default=None):
        """
        Return a value from the FieldStorage.

        If multiple values are available, only the first is returned. Attempts
        no decoding of string values.
        """
        if key in self._override:
            val = self._override[key]
            if isinstance(val, list):
                return val[0]
            return val
        return self._fs.getfirst(key, default)

    # get is an alias for getfirst
    get_raw = getfirst_raw

    def getlist_raw(self, key):
        """
        Return a list of values for key, even if there is only a single
        value available. Attempts no decoding of string values.
        """
        if key in self._override:
            val = self._override[key]
            if isinstance(val, basestring):
                return [val]
            try:
                iter(val)
            except:
                return [val]
            else:
                return val[0]
        return self._fs.getlist(key)

    def getfirst(self, key, default=None):
        """
        Return a value from the FieldStorage. If multiple values are available,
        only the first is returned. Decodes byte-strings values to unicode.
        """
        result = self.getfirst_raw(key, default)
        if isinstance(result, str):
            return self._decode_func(result)
        return result

    # get is an alias for getfirst
    get = getfirst

    def getlist(self, key):
        """
        Return a list of submitted values from the FieldStorage associated with
        the given key.
        Decodes byte-strings values to unicode.
        """
        return map(self._decode_func, self.getlist_raw(key))

    def getstorage(self, key, default=None):
        """
        Return the underlying cgi.FieldStorage item for ``key``. Will return
        ``default`` if there is no corresponding key in the form.

        This avoids all processing, and allows access to the lower-level
        features of cgi.FieldStorage, useful for processing file-uploads etc.
        """
        try:
            return self._fs[key]
        except KeyError:
            return default

    def has_key(self, key):
        """
        Return ``True`` if ``key`` exists in this object.
        """
        return key in self._fs or key in self._override

    def __contains__(self, key):
        """ True if ``key`` exists in this object """
        return key in self._fs or key in self._override

    def set(self, key, value):
        """ Set ``key`` to ``value``, masking any value from the request environment"""
        self._override[key] = value

class FileUpload(object):

    def __init__(self, fieldstorage):

        self.file = fieldstorage.file
        self.filename = fieldstorage.filename
        self.headers = fieldstorage.headers

        # UNC/Windows path
        if self.filename[:2] == r'\\' or self.filename[1:3] == r':\\':
            self.filename == self.filename[self.filename.rfind('\\')+1:]

    def save(self, fileob):

        if isinstance(fileob, basestring):
            fileob = open(fileob, "w")
            try:
                return self.save(fileob)
            finally:
                fileob.close()

        self.file.seek(0)
        while True:
            chunk = self.file.read(8192)
            if chunk == '':
                break
            fileob.write(chunk)

