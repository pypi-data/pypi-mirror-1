# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

"""
Utility functions for WSGI applications
"""

__docformat__ = 'restructuredtext en'
__all__ = [
    'use_x_forwarded', 'set_application_path', 'mount_app', 'use_redirect_url',
    'MockWSGI', 'make_absolute_url', 'run_with_cgi',
    'make_uri_component',
]

import inspect
import itertools
import os
import posixpath
import re
import sys
import unicodedata
import time

from cStringIO import StringIO
from urlparse import urlparse, urlunparse
from urllib import quote, quote_plus
from itertools import chain, repeat

try:
    from functools import wraps
except ImportError:
    # No-op for wraps in python <2.5
    wraps = lambda wrappedfunc: (
        lambda func: (
            lambda *args, **kwargs: func(*args, **kwargs)
        )
    )

from pesto.core import to_wsgi
from pesto.request import Request, DEFAULT_ENCODING

def use_x_forwarded(trusted=("127.0.0.1", "localhost")):
    """
    Return a middleware application that modifies the WSGI environment so that
    the X_FORWARDED_* headers are observed and generated URIs are correct in a
    proxied environment.

    Use this whenever the WSGI application server is sitting behind
    Apache or another proxy server.

    HTTP_X_FORWARDED_FOR is substituted for REMOTE_ADDR and
    HTTP_X_FORWARDED_HOST for SERVER_NAME. If HTTP_X_FORWARDED_SSL is set, then
    the wsgi.url_scheme is modified to ``https`` and ``HTTPS`` is set to
    ``on``.

    >>> from pesto.core import to_wsgi
    >>> from pesto.response import Response
    >>> from pesto.wsgiutils import MockWSGI
    >>> def app(request):
    ...     return Response(["URL is ", request.request_uri, "; REMOTE_ADDR is ", request.remote_addr])
    ...
    >>> app = use_x_forwarded()(to_wsgi(app))
    >>> mock = MockWSGI(
    ...     SERVER_NAME='wsgiserver-name',
    ...     SERVER_PORT='8080',
    ...     HTTP_HOST='wsgiserver-name:8080',
    ...     REMOTE_ADDR='127.0.0.1',
    ...     HTTP_X_FORWARDED_HOST='real-name:81',
    ...     HTTP_X_FORWARDED_FOR='1.2.3.4'
    ... )
    >>> ''.join(mock.run(app).output)
    'URL is http://real-name:81/; REMOTE_ADDR is 1.2.3.4'
    >>> mock = MockWSGI(
    ...     SERVER_NAME='wsgiserver-name',
    ...     SERVER_PORT='8080',
    ...     HTTP_HOST='wsgiserver-name:8080',
    ...     REMOTE_ADDR='127.0.0.1',
    ...     HTTP_X_FORWARDED_HOST='real-name:443',
    ...     HTTP_X_FORWARDED_FOR='1.2.3.4',
    ...     HTTP_X_FORWARDED_SSL='on'
    ... )
    >>> ''.join(mock.run(app).output)
    'URL is https://real-name/; REMOTE_ADDR is 1.2.3.4'
 
    In a non-forwarded environment, the environ dictionary will not be
    changed::
    >>> mock = MockWSGI(
    ...     SERVER_NAME='wsgiserver-name',
    ...     SERVER_PORT='8080',
    ...     HTTP_HOST='wsgiserver-name:8080',
    ...     REMOTE_ADDR='127.0.0.1',
    ... )
    >>> ''.join(mock.run(app).output)
    'URL is http://wsgiserver-name:8080/; REMOTE_ADDR is 127.0.0.1'
 
    """

    trusted = dict.fromkeys(trusted, None)
    def use_x_forwarded(app):
        def use_x_forwarded(environ, start_response):
            if environ.get('REMOTE_ADDR') in trusted:

                try:
                    environ['REMOTE_ADDR'] = environ['HTTP_X_FORWARDED_FOR']
                except KeyError:
                    pass

                is_ssl = bool(environ.get('HTTP_X_FORWARDED_SSL'))

                if 'HTTP_X_FORWARDED_HOST' in environ:
                    host = environ['HTTP_X_FORWARDED_HOST']

                    if ':' in host:
                        port = host.split(':')[1]
                    else:
                        port = is_ssl and '443' or '80'

                    environ['HTTP_HOST'] = host
                    environ['SERVER_PORT'] = port

                if is_ssl:
                    environ['wsgi.url_scheme'] = 'https'
                    environ['HTTPS'] = 'on'

            return app(environ, start_response)
        return use_x_forwarded
    return use_x_forwarded

def mount_app(appmap):
    """
    Create a composite application with different mount points.

    Synopsis::

        >>> def app1(e, sr):
        ...     return [1]
        ...
        >>> def app2(e, sr):
        ...     return [2]
        ...
        >>> app = mount_app({
        ...     '/path/one' : app1,
        ...     '/path/two' : app2,
        ... })
    """
    apps = appmap.items()
    apps.sort()
    apps.reverse()

    def mount_app(env, start_response):
        script_name = env.get("SCRIPT_NAME")
        path_info = env.get("PATH_INFO")
        for key, app in apps:
            if path_info[:len(key)] == key:
                app_env = env.copy()
                app_env["SCRIPT_NAME"] = script_name + key
                app_env["PATH_INFO"] = path_info[len(key):]
                if app_env["SCRIPT_NAME"] == "/":
                    app_env["SCRIPT_NAME"] = ""
                    app_env["PATH_INFO"] = "/" + app_env["PATH_INFO"]
                return app(app_env, start_response)
        else:
            start_response("404 Not Found", [])
            return [ "Not found"]

    return mount_app

def static_server(document_root, default_encoding="ISO-8859-1", BUFSIZE=8192):
    """
    Create a simple WSGI static file server application

    Synopsis::

        >>> from pesto.dispatch import urldispatcher
        >>> urldispatcher = urldispatcher()
        >>> urldispatcher.match('/static/<path:path>',
        ...     GET=static_server('/docroot'),
        ...     HEAD=static_server('/docroot')
        ... )
    """
    from pesto.response import Response

    document_root = os.path.abspath(os.path.normpath(document_root))

    @to_wsgi
    def static_server(request, path=None):

        if path is None:
            path = request.path_info

        path = posixpath.normpath(path)
        while path[0] == '/':
            path = path[1:]

        path = os.path.join(document_root, *path.split('/'))
        path = os.path.normpath(path)

        if not path.startswith(document_root):
            return Response.forbidden()
        return serve_static_file(request, path, default_encoding, BUFSIZE)

    return static_server

def serve_static_file(request, path, default_encoding="ISO-8859-1", BUFSIZE=8192):
    """
    Serve a static file located at ``path``. It is the responsibility of the
    caller to check that the path is valid and allowed.

    Synopsis::

        >>> from pesto.dispatch import urldispatcher
        >>> def view_important_document(request):
        ...     return serve_static_file(request, '/path/to/very_important_document.pdf')
        ...
        >>> def download_important_document(request):
        ...     return serve_static_file(request, '/path/to/very_important_document.pdf').add_headers(
        ...         content_disposition='attachment; filename=very_important_document.pdf'
        ...     )
        ...
    """
    import mimetypes
    from email.utils import parsedate
    from pesto.response import Response, STATUS_OK, STATUS_NOT_MODIFIED

    try:
        stat = os.stat(path)
    except OSError:
        return Response.not_found()

    mod_since = request.get_header('if-modified-since')

    if mod_since is not None:
        mod_since = time.mktime(parsedate(mod_since))
        if stat.st_mtime < mod_since:
            return Response(status=STATUS_NOT_MODIFIED)

    typ, enc = mimetypes.guess_type(path)
    if typ is None:
        typ = 'application/octet-stream'
    if typ.startswith('text/'):
        typ = typ + '; charset=%s' % default_encoding

    if 'wsgi.file_iterator' in request.environ:
        content_iterator = lambda fileob: request.environ['wsgi.file_iterator'](fileob, BUFSIZE)
    else:
        content_iterator = lambda fileob: ClosingIterator(iter(lambda: fileob.read(BUFSIZE), ''), fileob.close)
    try:
        _file = open(path, 'rb')
    except IOError:
        return Response.forbidden()

    return Response(
        status = STATUS_OK,
        content_length = str(stat.st_size),
        last_modified_date = time.strftime('%w, %d %b %Y %H:%M:%S GMT', time.gmtime(stat.st_mtime)),
        content_type = typ,
        content_encoding = enc,
        content = content_iterator(_file)
    )



def use_redirect_url(use_redirect_querystring=True):
    """
    Replace the ``SCRIPT_NAME`` and ``QUERY_STRING`` WSGI environment variables with
    ones taken from Apache's ``REDIRECT_URL`` and ``REDIRECT_QUERY_STRING`` environment
    variable, if set.

    If an application is mounted as CGI and Apache RewriteRules are used to
    route requests, the ``SCRIPT_NAME`` and ``QUERY_STRING`` parts of the environment
    may not be meaningful for reconstructing URLs.

    In this case Apache puts an extra key, ``REDIRECT_URL`` into the path which
    contains the full path as requested.

    See also:

        * `URL reconstruction section of PEP 333 <http://www.python.org/dev/peps/pep-0333/#url-reconstruction>`_.
        * `Apache mod_rewrite reference <http://httpd.apache.org/docs/2.0/mod/mod_rewrite.html>`_.

    **Example**: assume a handler similar to the below has been made available
    at the address ``/cgi-bin/myhandler.cgi``::

        >>> import pesto
        >>> from pesto.response import Response
        >>> def handler(request):
        ...     return Response([
        ...         request.script_name,
        ...         request.path_info,
        ...         request.request_uri,
        ...     ])
        >>> app = pesto.to_wsgi(handler)
 
    Apache has been configured to redirect requests
    using the following RewriteRules in a ``.htaccess`` file in the server's
    document root, or the equivalents in the apache configuration file::

        RewriteEngine On
        RewriteBase /
        RewriteRule ^pineapple(.*)$ /cgi-bin/myhandler.cgi [PT]

    The following code creates a simulation of the request headers Apache will pass to the application with the above rewrite rules::

        >>> mock = MockWSGI(
        ...     "http://example.com/myhandler.cgi/cake",
        ...     REDIRECT_URL = '/pineapple/cake',
        ...     SCRIPT_NAME = '/myhandler.cgi',
        ...     PATH_INFO = '/cake',
        ... )
        
    Without the middleware, the handler will output as follows::

        >>> mock.run(app).output
        ['/myhandler.cgi', '/cake', 'http://example.com/myhandler.cgi/cake']


    Use the ``use_redirect_url`` middleware to correctly set the
    ``SCRIPT_NAME`` and ``QUERY_STRING`` values::

        >>> app = use_redirect_url()(app)

    With this change the application will now output the correct values::

        >>> mock.run(app).output
        ['/pineapple', '/cake', 'http://example.com/pineapple/cake']

    """
    def use_redirect_url(wsgiapp):
        def use_redirect_url(env, start_response):
            if "REDIRECT_URL" in env:
                env['SCRIPT_NAME'] = env["REDIRECT_URL"]
                path_info = env["PATH_INFO"]
                if env["SCRIPT_NAME"][-len(path_info):] == path_info:
                    env["SCRIPT_NAME"] = env["SCRIPT_NAME"][:-len(path_info)]

            if use_redirect_querystring:
                if "REDIRECT_QUERY_STRING" in env:
                    env["QUERY_STRING"] = env["REDIRECT_QUERY_STRING"]
            return wsgiapp(env, start_response)
        return use_redirect_url
    return use_redirect_url

class MockWSGI(object):
    """
    A mock object for testing pesto components.

    Synopsis::

        >>> from pesto.core import to_wsgi
        >>> from pesto.response import Response
        >>> mock = MockWSGI('http://www.example.com/nelly')
        >>> mock.request.request_uri
        'http://www.example.com/nelly'
        >>> def app(request):
        ...     return Response(
        ...         content_type = 'text/html; charset=UTF-8',
        ...         x_whoa = 'Nelly',
        ...         content = ['Yop!']
        ...     )
        >>> mock.run(to_wsgi(app)) #doctest: +ELLIPSIS
        <pesto.wsgiutils.MockWSGI object at 0x...>
        >>> mock.headers
        [('Content-Type', 'text/html; charset=UTF-8'), ('X-Whoa', 'Nelly')]
        >>> mock.output
        ['Yop!']
        >>> print mock.raw_response
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        X-Whoa: Nelly\r
        \r
        Yop!
        >>>
    """

    def __init__(self, url=None, wsgi_input=None, SCRIPT_NAME='/', **environ):

        from pesto.response import Response

        self.status = None
        self.headers = None
        self.output = None
        self.exc_info = None
        if wsgi_input is not None:
            self.wsgi_input = wsgi_input
        else:
            self.wsgi_input = StringIO()
        self.wsgi_errors = StringIO()

        self.environ = {
            'REQUEST_METHOD'    : "GET",
            'SCRIPT_NAME'       : "/",
            'PATH_INFO'         : "",
            'QUERY_STRING'      : "",
            'CONTENT_TYPE'      : "",
            'CONTENT_LENGTH'    : "",
            'SERVER_NAME'       : "localhost",
            'SERVER_PORT'       : "80",
            'SERVER_PROTOCOL'   : "HTTP/1.0",
            'REMOTE_ADDR'       : "127.0.0.1",
            'wsgi.version'      : (1, 0),
            'wsgi.url_scheme'   : "http",
            'wsgi.input'        : self.wsgi_input,
            'wsgi.errors'       : self.wsgi_errors,
            'wsgi.multithread'  : False,
            'wsgi.multiprocess' : False,
            'wsgi.run_once'     : False,
        }
        self.mockapp = to_wsgi(lambda request: Response(['ok']))

        if url is not None:
            scheme, netloc, path, params, query, fragment = urlparse(url)
            if scheme is None:
                scheme = 'http'
            if netloc is None:
                netloc = 'example.org'
            if ':' in netloc:
                server, port = netloc.split(':')
            else:
                if scheme == 'https':
                    port = '443'
                else:
                    port = '80'
                server = netloc

            assert path.startswith(SCRIPT_NAME)
            PATH_INFO = path[len(SCRIPT_NAME):]
            if SCRIPT_NAME and SCRIPT_NAME[-1] == "/":
                SCRIPT_NAME = SCRIPT_NAME[:-1]
                PATH_INFO = "/" + PATH_INFO

            self.environ.update({
                'wsgi.url_scheme' : scheme,
                'SERVER_NAME'     : server,
                'SERVER_PORT'     : port,
                'SCRIPT_NAME'     : SCRIPT_NAME,
                'QUERY_STRING'    : query,
                'PATH_INFO'       : PATH_INFO,
            })

        self.environ.update(environ)

        if self.environ['SCRIPT_NAME'] == '/':
            self.environ['SCRIPT_NAME'] = ''
            self.environ['PATH_INFO'] = '/' + self.environ['PATH_INFO']

        self.request  = Request(self.environ)
        self.buf = StringIO()

    def start_response(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        if self.output:
            import logging
            logging.exception("start_response called after output started!")
            raise exc_info[0], exc_info[1], exc_info[2]
        self.exc_info = exc_info
        return self.buf.write

    def check_header(self, name, value):
        """
        Return true if value appears for the named response header
        """
        if self.headers is None:
            self.run(self.mockapp)
        return value in [ v for k, v in self.headers if k == name ]

    def get_header(self, name):
        """
        Return the value for the named response header, or None if it does not exist
        """
        if self.headers is None:
            self.run(self.mockapp)
        try:
            return [ v for k, v in self.headers if k == name ][0]
        except IndexError:
            return None

    def run_pesto(self, app):
        """
        Run the given pesto application.
        """
        return self.run(to_wsgi(app))

    def run(self, app):
        """
        Run the given WSGI application.
        """
        self.output = self.headers = self.status = None
        try:
            result = app(self.environ, self.start_response)
            if self.buf.getvalue():
                self.output = [self.buf.getvalue()] + list(result)
            else:
                self.output = list(result)
        finally:
            if hasattr(result, 'close'):
                result.close()
        return self

    def raw_response(self):
        r"""
        Return the raw response, incl. status line, headers and body, as would be sent by
        the webserver, in a single string.
        """

        if self.headers is None:
            self.run(self.mockapp)
        return '\r\n'.join(
            [self.status] + ['%s: %s' % item for item in self.headers] + ['', '']
        ) + ''.join(self.output)
    raw_response = property(raw_response)

    def content(self):
        """
        Content part as a single string
        """
        if self.headers is None:
            self.run(self.mockapp)
        return ''.join(self.output)
    content = property(content)

def mockwsgi_post(uri, data=None, content_type=None, encoding='UTF-8', **kwargs):
    """
    Convenience function for returning a ready-made MockWSGI post request.
    """
    if data is None:
        data = {}
    data.update(kwargs)
    if content_type is None:
        content_type = "application/x-www-form-urlencoded; charset=%s" % encoding

    data = make_query(data, encoding)
    return MockWSGI(uri, REQUEST_METHOD='POST', CONTENT_TYPE=content_type, CONTENT_LENGTH=len(data), wsgi_input=StringIO(data))

def mockwsgi_get(uri, data=None, encoding='UTF-8', content_type=None, **kwargs):
    """
    Convenience function for returning a ready-made MockWSGI get request.
    """
    if data is None:
        data = {}
    data.update(kwargs)

    scheme, netloc, path, params, query, fragment = urlparse(uri)
    if query is None:
        query = make_query(data)
    else:
        query = query + ';' + make_query(data, encoding)
    uri = urlunparse((scheme, netloc, path, params, query, fragment))
    if content_type is None:
        content_type = 'application/x-www-form-urlencoded; charset=%s' % encoding
    return MockWSGI(uri, REQUEST_METHOD='GET', CONTENT_TYPE=content_type)

def make_absolute_url(wsgi_environ, url):
    """
    Return an absolute url from ``url``, based on the current url.

    Synopsis::

        >>> environ = MockWSGI('https://example.com/foo').environ
        >>> make_absolute_url(environ, '/bar')
        'https://example.com/bar'
        >>> make_absolute_url(environ, 'baz')
        'https://example.com/foo/baz'
        >>> make_absolute_url(environ, 'http://anotherhost/bar')
        'http://anotherhost/bar'

    Note that the URL is constructed using the PEP-333 URL
    reconstruction method
    (http://www.python.org/dev/peps/pep-0333/#url-reconstruction) and the
    returned URL is normalized::

        >>> environ = MockWSGI(
        ...             'https://example.com/colors/red', 
        ...             SCRIPT_NAME='/colors',
        ...             PATH_INFO='/red'
        ... ).environ
        >>>
        >>> make_absolute_url(environ, '')
        'https://example.com/colors/red'
        >>> 
        >>> make_absolute_url(environ, 'blue')
        'https://example.com/colors/red/blue'
        >>> 
        >>> make_absolute_url(environ, '../blue')
        'https://example.com/colors/blue'
    
    """
    env = wsgi_environ.get
    if '://' not in url:
        scheme = env('wsgi.url_scheme', 'http')

        if scheme == 'https':
            port = ':' + env('SERVER_PORT', '443')
        else:
            port = ':' + env('SERVER_PORT', '80')

        if scheme == 'http' and port == ':80' or scheme == 'https' and port == ':443':
            port = ''

        parsed = urlparse(url)
        url = urlunparse((
            env('wsgi.url_scheme',''),
            env('HTTP_HOST', env('SERVER_NAME', '') + port),
            posixpath.abspath(
                posixpath.join(
                    quote(env('SCRIPT_NAME', '')) + quote(env('PATH_INFO', '')),
                    parsed[2]
                )
            ),
            parsed[3],
            parsed[4],
            parsed[5],
        ))
    return url

def uri_join(base, link):
    """
    >>> uri_join('http://example.org/', 'http://example.com/')
    'http://example.com/'

    >>> uri_join('http://example.com/', '../styles/main.css')
    'http://example.com/styles/main.css'

    >>> uri_join('http://example.com/subdir/', '../styles/main.css')
    'http://example.com/styles/main.css'

    >>> uri_join('http://example.com/login', '?error=failed+auth')
    'http://example.com/login?error=failed+auth'

    >>> uri_join('http://example.com/login', 'register')
    'http://example.com/register'
    """
    SCHEME, NETLOC, PATH, PARAM, QUERY, FRAGMENT = range(6)
    plink = urlparse(link)

    # Link is already absolute, return it unchanged
    if plink[SCHEME]:
        return link

    pbase = urlparse(base)
    path = pbase[PATH]
    if plink[PATH]:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(pbase[PATH]), plink[PATH]))

    return urlunparse((
        pbase[SCHEME],
        pbase[NETLOC],
        path,
        plink[PARAM],
        plink[QUERY],
        plink[FRAGMENT]
    ))

def _qs_frag(key, value, encoding=None):
    u"""
    Return a fragment of a query string in the format 'key=value'.

    >>> _qs_frag('search-by', 'author, editor')
    'search-by=author%2C+editor'

    If no encoding is specified, unicode values are encoded using the character set
    specified by ``pesto.request.DEFAULT_ENCODING``.
    """
    if encoding is None:
        encoding = DEFAULT_ENCODING

    return quote_plus(_make_bytestr(key, encoding)) \
            + '=' \
            + quote_plus(_make_bytestr(value, encoding))

def _make_bytestr(ob, encoding):
    u"""
    Return a byte string conversion of the given object. If the object is a
    unicode string, encode it with the given encoding.

    >>> _make_bytestr(1, 'utf-8')
    '1'
    >>> _make_bytestr(u'a', 'utf-8')
    'a'
    """
    if isinstance(ob, unicode):
        return ob.encode(encoding)
    return str(ob)

def _repeat_keys(iterable):
    u"""
    Return a list of ``(key, scalar_value)`` tuples given an iterable
    containing ``(key, iterable_or_scalar_value)``.

    >>> list(
    ...     _repeat_keys([('a', 'b')])
    ... )
    [('a', 'b')]
    >>> list(
    ...     _repeat_keys([('a', ['b', 'c'])])
    ... )
    [('a', 'b'), ('a', 'c')]
    """

    for key, value in iterable:
        if isinstance(value, basestring):
            value = [value]
        else:
            try:
                value = iter(value)
            except TypeError:
                value = [value]

        for subvalue in value:
            yield key, subvalue

def make_query(data=None, separator=';', encoding=None, **kwargs):
    """
    Return a query string formed from the given dictionary data.

    Note that the pairs are separated using a semicolon, in accordance with 
    `the W3C recommendation <http://www.w3.org/TR/1999/REC-html401-19991224/appendix/notes.html#h-B.2.2>`_

    If no encoding is given, unicode values are encoded using the character set
    specified by ``pesto.request.DEFAULT_ENCODING``.

    Synopsis::

        >>> # Basic usage
        >>> make_query({ 'eat' : u'more cake', 'drink' : u'more tea' })
        'drink=more+tea;eat=more+cake'

        >>> # Use an ampersand as the separator
        >>> make_query({ 'eat' : u'more cake', 'drink' : u'more tea' }, separator='&')
        'drink=more+tea&eat=more+cake'

        >>> # Can also be called using ``**kwargs`` style
        >>> make_query(eat=u'more cake', drink=u'more tea')
        'drink=more+tea;eat=more+cake'

        >>> # Non-string values
        >>> make_query(eat=[1, 2], drink=3.4)
        'drink=3.4;eat=1;eat=2'

        >>> # Multiple values per key
        >>> make_query(eat=[u'more', u'cake'], drink=u'more tea')
        'drink=more+tea;eat=more;eat=cake'

    """

    if data is None:
        data = {}
    data.update(kwargs)

    if encoding is None:
        encoding = DEFAULT_ENCODING

    items = data.items()
    # Sort data items for a predictable order in tests
    items.sort()
    items = _repeat_keys(items)
    return separator.join([
        _qs_frag(k, v, encoding=encoding) for k, v in items
    ])



def make_wsgi_environ_cgi():
    """
    Create a wsgi environment dictionary based on the CGI environment
    (taken from os.environ)
    """

    environ = dict(
        PATH_INFO = '',
        SCRIPT_NAME = '',
    )
    environ.update(os.environ)

    environ['wsgi.version'] = (1, 0)
    if environ.get('HTTPS','off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    environ['wsgi.input']        = sys.stdin
    environ['wsgi.errors']       = sys.stderr
    environ['wsgi.multithread']  = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once']     = True

    # PEP 333 insists that these be present and non-empty
    assert 'REQUEST_METHOD' in environ
    assert 'SERVER_PROTOCOL' in environ
    assert 'SERVER_NAME' in environ
    assert 'SERVER_PORT' in environ

    return environ

def run_with_cgi(application, environ=None):

    if environ is None:
        environ = make_wsgi_environ_cgi()

    headers_set = []
    headers_sent = []

    def write(data):
        if not headers_set:
            raise AssertionError("write() before start_response()")

        elif not headers_sent:
            # Before the first output, send the stored headers
            status, response_headers = headers_sent[:] = headers_set
            sys.stdout.write('Status: %s\r\n' % status)
            for header in response_headers:
                sys.stdout.write('%s: %s\r\n' % header)
            sys.stdout.write('\r\n')

        sys.stdout.write(data)
        sys.stdout.flush()

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None     # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]
        return write

    result = application(environ, start_response)
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()


def make_uri_component(s, separator="-"):
    """
    Turn a string into something suitable for a URI component.

    Synopsis::

        >>> import pesto.wsgiutils
        >>> pesto.wsgiutils.make_uri_component(u"How now brown cow")
        'how-now-brown-cow'


    Unicode characters are mapped to ASCII equivalents where appropriate, and
    characters which would normally have to be escaped are translated into
    hyphens to ease readability of the generated URI.

    s
        The (unicode) string to translate.

    separator
        A single ASCII character that will be used to replace spaces and other
        characters that are inadvisable in URIs.

    returns
        A lowercase ASCII string, suitable for inclusion as part of a URI.

    """
    if isinstance(s, unicode):
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    s = s.strip().lower()
    s = re.sub(r'[\s\/]+', separator, s)
    s = re.sub(r'[^A-Za-z0-9\-\_]', '', s)
    return s

def with_request_args(error_response=None,  **argspec):
    """
    Function decorator to map request query/form arguments to function arguments.

    Synopsis::

        >>> from pesto.dispatch import urldispatcher
        >>> from pesto import to_wsgi
        >>> from pesto.wsgiutils import MockWSGI
        >>> from pesto.response import Response
        >>>
        >>> dispatcher = urldispatcher()
        >>>
        >>> @dispatcher.match('/recipes/<category:unicode>/view', 'GET')
        ... @with_request_args(category=unicode, id=int)
        ... def my_handler(request, category, id):
        ...     return Response([
        ...         u'Recipe #%d in category "%s".' % (id, category)
        ...     ])
        >>> print MockWSGI('http://example.com/recipes/rat-stew/view?id=2').run(dispatcher).raw_response
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Recipe #2 in category "rat-stew".

    If specified arguments are not present in the request (and no default value
    is given in the function signature), or a TypeError or ValueError is thrown
    when performing type conversion, a ``400 Bad Request`` response will be
    given::

        >>> print MockWSGI('http://example.com/recipes/rat-stew/view').run(dispatcher).raw_response
        400 Bad Request\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        <html><body><h1>The server could not understand your request</h1></body></html>
 
    A default argument value in the handler function will protect against this::

        >>> dispatcher = urldispatcher()
        >>> @dispatcher.match('/recipes/<category:unicode>/view', 'GET')
        ... @with_request_args(category=unicode, id=int)
        ... def my_handler(request, category, id=1):
        ...     return Response([
        ...         u'Recipe #%d in category "%s".' % (id, category)
        ...     ])
        ... 
        >>> print MockWSGI('http://example.com/recipes/mouse-pie/view').run(dispatcher).raw_response
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        Recipe #1 in category "mouse-pie".
 
    Values which are present, but cannot be converted, will always trigger a
    ``400 Bad Request`` response::

        >>> print MockWSGI('http://example.com/recipes/mouse-pie/view?id=elephants').run(dispatcher).raw_response
        400 Bad Request\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        <html><body><h1>The server could not understand your request</h1></body></html>
 
    Sometimes it is necessary to map multiple request values to a single
    argument, for example in a form where two or more input fields have the
    same name. To do this, put the type-casting function into a list when
    calling ``with_request_args``::

        >>> @with_request_args(actions=[unicode])
        ... def my_handler(request, actions):
        ...     return Response([
        ...         u', '.join(actions)
        ...     ])
        ... 
        >>> app = to_wsgi(my_handler)
        >>> print MockWSGI('http://example.com/?actions=up;actions=up;actions=and+away%21').run(app).raw_response
        200 OK\r
        Content-Type: text/html; charset=UTF-8\r
        \r
        up, up, and away!

    """
    if error_response is None:
        from pesto.response import Response
        error_response = Response.bad_request

    def decorator(func):

        f_args, f_varargs, f_varkw, f_defaults = inspect.getargspec(func)

        for arg in argspec:
            if arg not in f_args:
                raise AssertionError('with_request_args parameter %r missing from function signature' % (arg,))

        # Produce a mapping of { argname: default }
        if f_defaults is None:
            f_defaults = []
        defaults = dict(zip(f_args[-len(f_defaults):], f_defaults))

        def decorated(*args, **kwargs):

            request = args[0]

            given_arguments = dict(
                zip(f_args[:len(args)], args)
            )
            given_arguments.update(kwargs)
            newargs = given_arguments.copy()


            for name, type_fn in argspec.items():
                try:
                    try:
                        value = given_arguments[name]
                    except KeyError:
                        if isinstance(type_fn, list):
                            value = request.form.getlist(name)
                        else:
                            value = request.form[name]

                    try:
                        if isinstance(type_fn, list):
                            value = [ cast(v) for cast, v in zip(itertools.cycle(type_fn), value) ]
                        else:
                            value = type_fn(value)
                    except (ValueError, TypeError):
                        return error_response()

                except KeyError:
                    try:
                        value = defaults[name]
                    except KeyError:
                        return error_response()
                newargs[name] = value

            return func(**newargs)

        return wraps(func)(decorated)

    return decorator

def overlay(*apps):
    u"""
    Run each application in turn and return the response from the first that
    does not return a 404 response.
    """

    from pesto.response import Response
    def app(environ, start_response):
        for app in apps:
            response = Response.from_wsgi(app, environ, start_response)
            if response.status[:3] != '404':
                return response(environ, start_response)
            else:
                response(environ, start_response).close()
        return Response.not_found()(environ, start_response)
    return app

class StartResponseWrapper(object):
    """
    Wrapper class for the ``start_response`` callable, which allows middleware
    applications to intercept and interrogate the proxied start_response arguments.

    Synopsis::

        >>> def my_wsgi_app(environ, start_response):
        ...     start_response('200 OK', [('Content-Type', 'text/plain')])
        ...     return ['Whoa nelly!']
        ...
        >>> def my_other_wsgi_app(environ, start_response):
        ...     responder = StartResponseWrapper(start_response)
        ...     result = my_wsgi_app(environ, responder)
        ...     print "Got status", responder.status
        ...     print "Got headers", responder.headers
        ...     responder.call_start_response()
        ...     return result
        ...
        >>> result = MockWSGI().run(my_other_wsgi_app)
        Got status 200 OK
        Got headers [('Content-Type', 'text/plain')]

    See also ``Response.from_wsgi``, which takes a wsgi callable, environ and
    start_response, and returns a ``Response`` object, allowing the client to
    further interrogate and customize the WSGI response.

    Note that it is usually not advised to use this directly in middleware as
    start_response may not be called directly from the WSGI application, but
    rather from the iterator it returns. In this case the middleware may need
    logic to accommodate this. It is usually safer to use
    ``Response.from_wsgi``, which takes this into account.
    """

    def __init__(self, start_response):
        self.start_response = start_response
        self.status = None
        self.headers = []
        self.called = False
        self.buf = StringIO()

    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        self.called = True
        return self.buf.write

    def call_start_response(self):
        try:
            write = self.start_response(
                self.status,
                self.headers,
                self.exc_info
            )
            write(self.buf.getvalue())
            return write
        finally:
            # Avoid dangling circular ref
            self.exc_info = None

class ClosingIterator(object):
    """
    Wrap an WSGI iterator to allow additional close functions to be called on
    application exit.

    Synopsis::

        >>> class filelikeobject(object):
        ...
        ...     def read(self):
        ...         print "file read!"
        ...         return ''
        ...
        ...     def close(self):
        ...         print "file closed!"
        ...
        >>> def app(environ, start_response):
        ...     f = filelikeobject()
        ...     start_response('200 OK', [('Content-Type: text/plain')])
        ...     return ClosingIterator(iter(f.read, ''), f.close)
        ...
        >>> m = MockWSGI().run(app)
        file read!
        file closed!

    """

    def __init__(self, iterable, *close_funcs):
        self._iterable = iterable
        self._next = iter(self._iterable).next
        self._close_funcs = close_funcs
        iterable_close = getattr(self._iterable, 'close', None)
        if iterable_close:
            self._close_funcs = (iterable_close,) + close_funcs
        self._closed = False

    def __iter__(self):
        return self

    def next(self):
        return self._next()

    def close(self):
        self._closed = True
        for func in self._close_funcs:
            func()

    def __del__(self):
        if not self._closed:
            import warnings
            warnings.warn("%r deleted without close being called" % (self,))

class MultiDict(dict):
    """
    Like a dictionary, but supports multiple values per key.

    Synopsis::

        >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        >>> d['a']
        1
        >>> d['b']
        3
        >>> d.getlist('a')
        [1, 2]
        >>> d.getlist('b')
        [3]

    """

    def __init__(self, posarg=None, **kwargs):
        """
        MultiDicts can be constructed in the following ways:

            1. From a sequence of ``(key, value)`` pairs::

                >>> MultiDict([('a', 1), ('a', 2)])
                MultiDict([('a', 1), ('a', 2)])

            2. Initialized from another MultiDict::

                >>> d = MultiDict([('a', 1), ('a', 2)])
                >>> MultiDict(d)
                MultiDict([('a', 1), ('a', 2)])

            3. Initialized from a regular dict::

                >>> MultiDict({'a': 1})
                MultiDict([('a', 1)])

            4. From keyword arguments::

                >>> MultiDict(a=1)
                MultiDict([('a', 1)])

        """
        dict.__init__(self)

        if posarg is None:
            posarg = []

        if isinstance(posarg, self.__class__):
            posarg = posarg.iterallitems()

        if isinstance(posarg, dict):
            posarg = posarg.items()

        for key, value in chain(posarg, kwargs.items()):
            dict.setdefault(self, key, []).append(value)

    def __getitem__(self, key):
        """
        Return the first item associated with ``key``::

            >>> d = MultiDict([('a', 1), ('a', 2)])
            >>> d['a']
            1
        """
        try:
            return dict.__getitem__(self, key)[0]
        except IndexError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Set the items associated to a list of one item, ``value``.

            >>> d = MultiDict()
            >>> d['b'] = 3
            >>> d
            MultiDict([('b', 3)])
        """
        return dict.__setitem__(self, key, [value])

    def get(self, key, default=None):
        try:
            return dict.get(self, key, [])[0]
        except IndexError:
            return default

    def getlist(self, key):
        return dict.get(self, key, [])

    def copy(self):
        """
        Return a shallow copy of the dictionary::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy = d.copy()
            >>> copy
            MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy is d
            False
        """
        return MultiDict(self)


    def fromkeys(cls, seq, value=None):
        """
        Create a new MultiDict with keys from seq and values set to value.

            >>> MultiDict.fromkeys(['a', 'b'])
            MultiDict([('a', None), ('b', None)])

        Keys can be repeated::

            >>> d = MultiDict.fromkeys(['a', 'b', 'a'])
            >>> d.getlist('a')
            [None, None]
            >>> d.getlist('b')
            [None]

        """
        return cls(zip(seq, repeat(value)))
    fromkeys = classmethod(fromkeys)

    def items(self):
        """
        >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        >>> sorted(d.items())
        [('a', 1), ('b', 3)]
        """
        return list(self.iteritems())

    def iteritems(self):
        for key in self.iterkeys():
            yield key, self[key]

    def listitems(self):
        """
        Like ``items``, but returns lists of values::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.listitems())
            [('a', [1, 2]), ('b', [3])]
        """
        return dict.items(self)

    def iterlistitems(self):
        return dict.iteritems(self)

    def allitems(self):
        """
        Return a list of ``(key, value)`` pairs for each item in the MultiDict.
        Items with multiple keys will have multiple key-value pairs returned::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.allitems())
            [('a', 1), ('a', 2), ('b', 3)]
        """
        return list(self.iterallitems())

    def iterallitems(self):
        for key, values in dict.iteritems(self):
            for value in values:
                yield key, value

    def values(self):
        """
        >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        >>> sorted(d.values())
        [1, 3]
        """
        return list(self.itervalues())

    def itervalues(self):
        for key in self.iterkeys():
            yield self[key]

    def listvalues(self):
        """
        Like ``values``, but returns lists of values::

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> sorted(d.listvalues())
            [[1, 2], [3]]
        """
        return list(self.iterlistvalues())

    def iterlistvalues(self):
        return dict.itervalues(self)

    def pop(self, key, default=None):
        try:
            return dict.pop(self, key, default)[0]
        except IndexError:
            raise KeyError(key)

    def popitem(self):
        try:
            return dict.pop(self)[0]
        except IndexError:
            raise KeyError()

    def setdefault(self, key, default=None):
        return dict.setdefault(self, key, [default])[0]

    def update(self, other=None, **kwargs):
        """
        Update the MultiDict from another MultiDict::

                >>> d = MultiDict()
                >>> d.update(MultiDict([('a', 1), ('a', 2)]))
                >>> d
                MultiDict([('a', 1), ('a', 2)])
            
        dictionary::

                >>> d = MultiDict()
                >>> d.update({'a': 1, 'b': 2})
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        iterable of key, value pairs::

                >>> d = MultiDict()
                >>> d.update([('a', 1), ('b', 2)])
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        Note that in this case, repeated keys in the iterable are ignored. The
        effect is the same as calling ``update`` once for each repeated key::

                >>> d = MultiDict()
                >>> d.update([('a', 1), ('a', 2)])
                >>> d
                MultiDict([('a', 2)])
             
        or keyword arguments::

                >>> d = MultiDict()
                >>> d.update(a=1, b=2)
                >>> d
                MultiDict([('a', 1), ('b', 2)])

        """
        if other is None:
            items = []
        elif isinstance(other, self.__class__):
            items = other.iterlistitems()
        elif isinstance(other, dict):
            items = [(key, [item]) for key, item in other.iteritems()]
        else:
            items = [(key, [item]) for key, item in iter(other)]

        items = chain(items, [(key, [item]) for key, item in kwargs.iteritems()])

        for key, values in items:
            dict.__setitem__(self, key, values)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.allitems())

    def __str__(self):
        return repr(self)

