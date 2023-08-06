# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__docformat__ = 'restructuredtext en'

__all__ = [
    'urldispatcher', 'NamedURLNotFound',
    'URLGenerationError'
]

import logging
import re
import types

from urllib import unquote

try:
    from functools import partial
except ImportError:
    from pesto.utils import partial

import pesto
import pesto.lrucache
import pesto.core
from pesto.core import PestoWSGIApplication
from pesto.response import Response
from pesto.request import Request, DEFAULT_ENCODING

class URLGenerationError(Exception):
    pass

class Pattern(object):

    def test(self, url):
        """
        Should return a tuple of ``(positional_arguments, keyword_arguments)`` if the
        pattern matches the given URL, or None if it does not match.
        """
        raise NotImplementedError

    def pathfor(self, *args, **kwargs):
        """
        The inverse of ``test``: where possible, should generate a URL for the
        given positional and keyword arguments.
        """
        raise NotImplementedError

class Converter(object):
    """
    Responsible for converting arguments to and from URI components.

    A ``Converter`` class has two instance methods:

        ``to_string`` - convert from a python object to a string
        ``from_string`` - convert from URI-encoded bytestring to the target python type.

    It must also define the regular expression pattern that is used to extract
    the string from the URI.
    """


    pattern = '[^/]+'

    def __init__(self, pattern=None):
        if pattern is not None:
            self.pattern = pattern

    def to_string(self, s):
        return unicode(s)

    def from_string(self, s):
        raise NotImplementedError


class IntConverter(Converter):

    pattern = r'[+-]?\d+'

    def from_string(self, s):
        return int(s)


class UnicodeConverter(Converter):

    pattern = r'[^/]+'

    def to_string(self, s):
        return s

    def from_string(self, s):
        return unicode(s)

class AnyConverter(UnicodeConverter):

    pattern = r'[+-]?\d+'

    def __init__(self, *args):
        if len(args) == 0:
            raise ValueError("Must supply at least one argument to any()")
        self.pattern = '|'.join(re.escape(arg) for arg in args)

class PathConverter(UnicodeConverter):

    pattern = r'.+'


class ExtensiblePattern(Pattern):
    """
    An extensible URL pattern matcher.

    Synopsis::

        >>> p = ExtensiblePattern(r"/archive/<year:int>/<month:int>/<title:unicode>")
        >>> p.test('/archive/1999/02/blah') == ((), {'year': 1999, 'month': 2, 'title': 'blah'})
        True

    Patterns are split on slashes into components. A component can either be a
    literal part of the path, or a pattern component in the form::

        <identifier> : <regex> : <converter>

    ``identifer`` can be any python name, which will be used as the name of a
    keyword argument to the matched function. If omitted, the argument will be
    passed as a positional arg.

    ``regex`` can be any regular expression pattern. If omitted, the
    converter's default pattern will be used.

    ``converter`` must be the name of a pre-registered converter. Converters
    must support ``to_string`` and ``from_string`` methods and are used to convert
    between URL segments and python objects.

    By default, the following converters are configured:

        * ``int`` - converts to an integer
        * ``path`` - any path (ie can include forward slashes)
        * ``unicode`` - any unicode string (not including forward slashes)
        * ``any`` - a string matching a list of alternatives

    Some examples::

        >>> p = ExtensiblePattern(r"/images/<:path>")
        >>> p.test('/images/thumbnails/02.jpg')
        ((u'thumbnails/02.jpg',), {})

        >>> p = ExtensiblePattern("/<page:any('about', 'help', 'contact')>.html")
        >>> p.test('/about.html')
        ((), {'page': u'about'})

        >>> p = ExtensiblePattern("/entries/<id:int>")
        >>> p.test('/entries/23')
        ((), {'id': 23})


    Others can be added by calling ``ExtensiblePattern.register_converter``
    """

    preset_patterns = (
        ('int', IntConverter),
        ('unicode', UnicodeConverter),
        ('path', PathConverter),
        ('any', AnyConverter),
    )
    pattern_parser = re.compile("""
        <
            (?P<name>\w[\w\d]*)?
            :
            (?P<converter>\w[\w\d]*)
            (?:
                \(
                         (?P<args>.*?)
                \)
            )?
        >
    """, re.X)

    class Segment(object):

        def __init__(self, source, regex, name, converter):
            self.source = source
            self.regex = regex
            self.name = name
            self.converter = converter

    def __init__(self, pattern, name=''):

        self.name = name
        self.preset_patterns = dict(self.__class__.preset_patterns)
        self.pattern = unicode(pattern)

        self.segments = list(self._make_segments(pattern))
        self.args = [ item for item in self.segments if item.converter is not None ]
        self.regex = re.compile(''.join([ segment.regex for segment in self.segments]) + '$')

    def _make_segments(self, s):
        r"""
        Generate successive Segment objects from the given string.

        Each segment object represents a part of the pattern to be matched, and
        comprises ``source``, ``regex``, ``name`` (if a named parameter) and
        ``converter`` (if a parameter)
        """

        for item in split_iter(self.pattern_parser, self.pattern):
            if isinstance(item, unicode):
                yield self.Segment(item, re.escape(item), None, None)
                continue
            groups = item.groupdict()
            name, converter, args = groups['name'], groups['converter'], groups['args']
            if isinstance(name, unicode):
                # Name must be a Python identifiers 
                name = name.encode("ASCII")
            converter = self.preset_patterns[converter]
            if args:
                args, kwargs = self.parseargs(args)
                converter = converter(*args, **kwargs)
            else:
                converter = converter()
            yield self.Segment(item.group(0), '(%s)' % converter.pattern, name, converter)

    def parseargs(self, argstr):
        """
        Return a tuple of ``(args, kwargs)`` parsed out of a string in the format ``arg1, arg2, param=arg3``.

        Synopsis::

            >>> ep =  ExtensiblePattern('')
            >>> ep.parseargs("1, 2, 'buckle my shoe'")
            ((1, 2, 'buckle my shoe'), {})
            >>> ep.parseargs("3, four='knock on the door'")
            ((3,), {'four': 'knock on the door'})

        """
        return eval('(lambda *args, **kwargs: (args, kwargs))(%s)' % argstr)

    def test(self, uri):
        mo = self.regex.match(uri)
        if not mo:
            return None
        groups = mo.groups()
        assert len(groups) == len(self.args), (
                "Number of regex groups does not match expected count. "
                "Perhaps you have used capturing parentheses somewhere? "
                "The pattern tested was %r." % self.regex.pattern
        )

        try:
            groups = [
                (segment.name, segment.converter.from_string(value))
                  for value, segment in zip(groups, self.args)
            ]
        except ValueError:
            return None

        args = tuple([value for name, value in groups if not name ])
        kwargs = dict([(name, value) for name, value in groups if name])
        return args, kwargs

    def pathfor(self, *args, **kwargs):
        """
        >>> p = ExtensiblePattern("/view/<filename:unicode>/<revision:int>")
        >>> p.pathfor(filename='important_document.pdf', revision=299)
        u'/view/important_document.pdf/299'

        >>> p = ExtensiblePattern("/view/<:unicode>/<:int>")
        >>> p.pathfor('important_document.pdf', 299)
        u'/view/important_document.pdf/299'
        """

        args = list(args)
        result = []
        for segment in self.segments:
            if not segment.converter:
                result.append(segment.source)
            elif segment.name:
                try:
                    result.append(segment.converter.to_string(kwargs[segment.name]))
                except IndexError, e:
                    raise URLGenerationError("Argument %r not specified for url %r" % (name, self.pattern))
            else:
                try:
                    result.append(segment.converter.to_string(args.pop(0)))
                except IndexError, e:
                    raise URLGenerationError("Not enough positional arguments for url %r" % (self.pattern,))
        return ''.join(result)

    @classmethod
    def register_converter(cls, name, converter):
        """
        Register a preset pattern for later use in URL patterns.

            >>> from datetime import date
            >>> from time import strptime
            >>> class DateConverter(Converter):
            ...     pattern = r'\d{8}'
            ...     def from_string(self, s):
            ...         return date(*strptime(s, '%d%m%Y')[:3])
            ... 
            >>> ExtensiblePattern.register_converter('date', DateConverter)
            >>> ExtensiblePattern('/<:date>').test('/01011970')
            ((datetime.date(1970, 1, 1),), {})
        """
        cls.preset_patterns += ((name, converter),)

    def __str__(self):
        return '<%s %r>' % (self.__class__, self.pattern)

class urldispatcher(object):
    """
    Match URLs to pesto handlers.

    Use the ``match``, ``imatch`` and ``matchre`` methods to associate URL
    patterns and HTTP methods to callables::

        >>> import pesto.dispatch
        >>> from pesto.response import Response
        >>> dispatcher = pesto.dispatch.urldispatcher()
        >>> def search_form(request):
        ...     return Response(['Search form page'])
        ... 
        >>> def do_search(request):
        ...     return Response(['Search page'])
        ... 
        >>> def faq(request):
        ...     return Response(['FAQ page'])
        ... 
        >>> def faq_category(request):
        ...     return Response(['FAQ category listing'])
        ... 
        >>> dispatcher.match("/search", GET=search_form, POST=do_search)
        >>> dispatcher.match("/faq", GET=faq)
        >>> dispatcher.match("/faq/<category:unicode>", GET=faq_category)

    The last matching pattern wins.

    Patterns can also be named so that they can be retrieved using the urlfor method::

        >>> from pesto.wsgiutils import MockWSGI
        >>> mock = MockWSGI('http://example.com/')
        >>> dispatcher = pesto.dispatch.urldispatcher()
        >>> dispatcher.matchpattern(
        ...     ExtensiblePattern("/faq/<category:unicode>"), 'faq_category', None, GET=faq_category
        ... )
        >>> dispatcher.urlfor('faq_category', category='foo')
        'http://example.com/faq/foo'

    Decorated handler functions also grow a ``url`` method that generates valid
    URLs for the function::

        >>> from pesto.wsgiutils import MockWSGI
        >>> mock = MockWSGI('http://example.com/')
        >>> @dispatcher.match("/faq/<category:unicode>", "GET")
        ... def faq_category(request, category):
        ...     return ['content goes here']
        ... 
        >>> faq_category.url(category='alligator')
        'http://example.com/faq/alligator'

    """

    default_pattern_type = ExtensiblePattern

    def __init__(self, cache_size=0, debug=False, strip_trailing_slash=True):
        """
        Create a new urldispatcher.

        ``cache_size``
            if non-zero, a least recently used (lru) cache of this size will be
            maintained, mapping URLs to callables.

        ``strip_trailing_slash``
            if True, any request ending in a trailing slash will have this
            stripped before patterns are applied.
        """
        self.patterns = []
        self.named_patterns = {}
        self.strip_trailing_slash = strip_trailing_slash
        self.debug = debug
        self._cache = None
        if cache_size > 0:
            self._cache = pesto.lrucache.LRUCache(cache_size)
            self.gettarget = self._cached_gettarget

    def status404_application(self, request):
        """
        Return a ``404 Not Found`` response.

        Called when the dispatcher cannot find a matching URI.
        """
        return Response.not_found()

    def status405_application(self, request, valid_methods):
        """
        Return a ``405 Method Not Allowed`` response.

        Called when the dispatcher can find a matching URI, but the HTTP
        methods do not match.
        """

        return Response.method_not_allowed(valid_methods)

    def matchpattern(self, pattern, name, predicate, *args, **dispatchers):
        """
        Match a URL with the given pattern, specified as an instance of ``Pattern``.

            pattern
                A pattern object, eg ``ExtensiblePattern('/pages/<name:unicode>')``

            name
                A name that can be later used to retrieve the url with ``urlfor``, or ``None``

            predicate
                A callable that is used to decide whether to match this
                pattern, or ``None``.
                Must take a ``Request`` object as its only parameter and
                return ``True`` or ``False``.

        Synopsis::

            >>> from pesto.response import Response
            >>> dispatcher = urldispatcher()
            >>> def view_items(request, tag):
            ...     return Response(["yadda yadda yadda"])
            ...
            >>> dispatcher.matchpattern(
            ...     ExtensiblePattern(
            ...          "/items-by-tag/<tag:unicode>",
            ...     ),
            ...     'view_items',
            ...     None,
            ...     GET=view_items
            ... )

        URLs can later be generated with the urlfor method on the dispatcher
        object::

            >>> Response.redirect(dispatcher.urlfor(
            ...     'view_items',
            ...     tag='spaghetti',
            ... ))                                      # doctest: +ELLIPSIS
            <pesto.response.Response object at ...>

        Or, if used in the second style as a function decorator, by
        calling the function's ``.url`` method::

            >>> @dispatcher.match('/items-by-tag/<tag:unicode>', 'GET')
            ... def view_items(request, tag):
            ...     return Response(["yadda yadda yadda"])
            ...
            >>> Response.redirect(view_items.url(tag='spaghetti')) # doctest: +ELLIPSIS
            <pesto.response.Response object at ...>

        Note that the ``url`` function can take optional query and fragment
        paraments to help in URL construction::

            >>> from pesto.wsgiutils import MockWSGI
            >>> from pesto.dispatch import urldispatcher
            >>> 
            >>> dispatcher = urldispatcher()
            >>>
            >>> request = MockWSGI('http://localhost/').request
            >>> @dispatcher.match('/pasta', 'GET')
            ... def pasta(request):
            ...     return Response(["Tasty spaghetti!"])
            ...
            >>> pasta.url(query={'sauce' : 'ragu'}, fragment='eat')
            'http://localhost/pasta?sauce=ragu#eat'
        """

        if dispatchers:
            if name:
                self.named_patterns[name] = (pattern, predicate, dispatchers)
            self.patterns.insert(0, (pattern, predicate, dispatchers))

        elif args:
            import pesto
            def decorator(func):
                self.patterns.insert(0, (pattern, predicate, dict([(method, func) for method in args])))
                pathfor = self.patterns[0][0].pathfor
                def url(request=None, query='', fragment='', *args, **kwargs):
                    if request is None:
                        request = pesto.currentrequest()
                    return request.make_uri(
                        path=request.script_name + pathfor(*args, **kwargs),
                        parameters='', query=query, fragment=fragment
                    )
                func.url = url

                return func
            return decorator
        else:
            raise URLGenerationError("HTTP methods not specified")

    def match(self, pattern, *args, **dispatchers):
        """
        Match the given URL using the default pattern type
        """
        name = dispatchers.pop('name', None)
        predicate = dispatchers.pop('predicate', None)
        return self.matchpattern(self.default_pattern_type(pattern), name, predicate, *args, **dispatchers)

    def methodsfor(self, path):
        """
        Return a list of acceptable HTTP methods for the given path
        """
        methods = {}
        for p, predicate, dispatchers in self.patterns:
            match, params = p.test(path)
            if match:
                for meth in dispatchers:
                    methods[meth] = None

        return methods.keys()

    def urlfor(self, _dispatcher_name, request=None, *args, **kwargs):
        """
        Map a handler back to a url.
        """
        import pesto
        if request is None:
            request = pesto.currentrequest()
        if _dispatcher_name not in self.named_patterns:
            raise NamedURLNotFound(_dispatcher_name)
        pattern, predicate, handlers = self.named_patterns[_dispatcher_name]
        try:
            handler = handlers['GET']
        except KeyError:
            handler = handlers.values()[0]
        return request.make_uri(
                path=request.script_name + pattern.pathfor(*args, **kwargs),
                parameters='', query='', fragment=''
        )

    def _cached_gettarget(self, path, method, request):

        request.environ['pesto.urldispatcher'] = self
        while self.strip_trailing_slash and len(path) > 1 and path[-1] == u'/':
            path = path[:-1]

        try:
            return self._cache[(path, method)]
        except KeyError:
            targets = self._cache[(path, method)] = list(self._gettarget(path, method, request))
            return targets

    def gettarget(self, path, method, request, start_from=None):
        """
        Yield dispatch targets methods matching the request URI. For each
        function matched, yield the function and a dictionary of keyword
        arguments taken from the URI.

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> from pesto.dispatch import urldispatcher
            >>> 
            >>> d = urldispatcher()

            >>> def show_entry(request):
            ...     return [ "Show entry page" ]
            ... 
            >>> def new_entry_form(request):
            ...     return [ "New entry form" ]
            ... 

            >>> d.match(r'/entries/<id:unicode>', GET=show_entry)
            >>> d.match(r'/entries/new',          GET=new_entry_form)

            >>> request = MockWSGI('http://localhost/entries/foo').request
            >>> list(d.gettarget(u'/entries/foo', 'GET', request))  # doctest: +ELLIPSIS
            [(<function show_entry ...>, (), {'id': u'foo'})]

            >>> request = MockWSGI('http://localhost/entries/new').request
            >>> list(d.gettarget(u'/entries/new', 'GET', request)) #doctest: +ELLIPSIS
            [(<function new_entry_form ...>, (), {}), (<function show_entry ...>, (), {'id': u'new'})]
            
        """
        request.environ['pesto.urldispatcher'] = self
        while self.strip_trailing_slash and len(path) > 1 and path[-1] == u'/':
            path = path[:-1]

        if self.debug:
            logging.debug("gettarget: path is: %r", path)

        return self._gettarget(path, method, request)

    def _gettarget(self, path, method, request):
        if self.debug:
            logging.debug("_gettarget: %s %r", method, path)

        for p, predicate, dispatchers in self.patterns:
            result = p.test(path)
            if self.debug:
                logging.debug("_gettarget: testing against %r", str(p))
            if result is None:
                continue
            if predicate is not None and not predicate(request):
                continue
            positional_args, keyword_args = result
            if self.debug and method in dispatchers:
                logging.debug("_gettarget: matched path to %r", dispatchers[method])
            try:
                target = dispatchers[method]
                if isinstance(target, types.UnboundMethodType):
                    target = getattr(target.im_class(), target.__name__)
                yield target, positional_args, keyword_args
            except KeyError:
                request.environ.setdefault('pesto.urldispatcher.valid_methods', []).extend(dispatchers.keys())
                if self.debug:
                    logging.debug("_gettarget: invalid method for pattern %s: %s", p, method)
        else:
            if self.debug:
                logging.debug("_gettarget: no match for path %r", path)

        raise StopIteration

    def combine(self, *others):
        """
        Add the patterns from dispatcher ``other`` to this dispatcher.

        Synopsis::

            >>> from pesto.wsgiutils import MockWSGI
            >>> d1 = urldispatcher()
            >>> d1.match('/foo', GET=lambda request: Response(['d1:foo']))
            >>> d2 = urldispatcher()
            >>> d2.match('/bar', GET=lambda request: Response(['d2:bar']))
            >>> combined = urldispatcher().combine(d1, d2)
            >>> MockWSGI('/foo').run(combined).content
            'd1:foo'
            >>> MockWSGI('/bar').run(combined).content
            'd2:bar'

        Note settings other than patterns are not carried over from the other
        dispatchers - if you intend to use the debug flag or caching options,
        you must explicitly set them in the combined dispatcher::

            >>> combined = urldispatcher(debug=True, cache_size=50).combine(d1, d2)
            >>> MockWSGI('/foo').run(combined).content
            'd1:foo'
        """
        for other in others:
            if not isinstance(other, urldispatcher):
                raise TypeError("Can only combine with other urldispatchers")

            self.patterns += other.patterns
        return self

    def __call__(self, environ, start_response):

        request = Request(environ)
        method = request.request_method.upper()
        path = unquote(request.decode(request.path_info))

        if path == u'' or path is None:
            path = u'/'

        for handler, args, kwargs in self.gettarget(path, method, request):
            environ['wsgiorg.routing_args'] = (args, kwargs)
            return PestoWSGIApplication(handler, *args, **kwargs)(environ, start_response)
        try:
            del environ['wsgiorg.routing_args']
        except KeyError:
            pass

        if 'pesto.urldispatcher.valid_methods' in environ:
            return self.status405_application(request, environ['pesto.urldispatcher.valid_methods'])(environ, start_response)
        else:
            return self.status404_application(request)(environ, start_response)

def split_iter(pattern, string):
    """
    Generate alternate strings and match objects for all occurances of
    ``pattern`` in ``string``.
    """
    matcher = pattern.finditer(string)
    match = None
    pos = 0
    for match in matcher:
        yield string[pos:match.start()]
        yield match
        pos = match.end()
    yield string[pos:]


class NamedURLNotFound(Exception):
    """
    Raised if the named url can't be found (eg in ``urlfor``).
    """
