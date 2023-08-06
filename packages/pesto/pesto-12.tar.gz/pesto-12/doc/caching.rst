
Caching
=======

.. testsetup:: *

        from pesto.testing import TestApp

Pesto contains support for setting and parsing cache control headers, including
entity tags (ETags).


Cache control headers
---------------------

The ``pesto.caching.no_cache`` decorator modifies response headers to instruct
browsers and caching proxies not to cache a page. See the module API docs
(below) for sample usage.

ETags
-----

The minimum you need to know about ETags
``````````````````````````````````````````

ETags are HTTP headers sent by a HTTP server indicating a revision of a
document. Typically a web server will supply an ETag along with the content on
the first request. Sample HTTP response headers including an etag might look
like this::

        200 OK
        Content-Type: text/html; charset=UTF-8
        ETag: "xyzzy"

When the browser makes subsequent requests for the same URL, it will
send an ``If-None-Match`` header::

        GET /index.html HTTP/1.1
        If-None-Match: "xyzzy"

The server can then compare the ``If-None-Match`` ETag value with the current
value. If they match then rather than serving the content again, the server can
reply with a ``304 Not Modified`` status, and the browser will display a cached
version.

Any string can be used as an ETag. When serving static content you could use a
concatenate the file's inode, filesize and modification time to generate an
ETag – this is what Apache does. Alternatives include a using an incrementing
sequence number or a string that represents an object's state in memory.

ETags come in two flavours: strong and weak. The above examples show strong
ETags. A weak ETag looks much the same, but has a ``W/`` prefix::

        ETag: W/"notsostrong"

A weak ETag signifies that the content is semantically equivalent, even if the
byte-for-byte representation may have changed. The HTTP RFC gives an example of
a hit counter image, which does not absolutely need to be refreshed by the
client on every request.

How to add ETag support
````````````````````````

Let's build a hit counter application. Here's a version without ETag support.
You'll need the Python Image library installed to try this example. Also note
that this is a very simplified example that would not be
suitable for use for a real application:

.. testcode::

        import Image
        import ImageDraw
        from StringIO import StringIO
        from pesto import to_wsgi
        from pesto.response import Response

        class HitCounter(object):

                current_count = 0

                def counter(self, request):

                        self.current_count += 1

                        img = Image.new('RGB', (50, 30))
                        draw = ImageDraw.Draw(img)
                        draw.text((10, 10), str(self.current_count))
                        buf = StringIO()
                        img.save(buf, 'PNG')

                        return Response(
                                [buf.getvalue()],
                                content_type='image/png'
                        )

        if __name__ == '__main__':
                from wsgiref.simple_server import make_server
                counter = HitCounter()
                app = to_wsgi(counter.counter)
                httpd = make_server('', 8000, app)
                print "Now load http://localhost:8000/ in a web browser"
                httpd.serve_forever()

.. doctest::
        :hide:

        >>> counter = HitCounter()
        >>> app = to_wsgi(counter.counter)
        >>> print TestApp(app).get().text().decode('ascii', 'ignore')
        200 OK
        Content-Type: image/png
        <BLANKLINE>
        ...


Save and run this script, then browse to http://localhost:8000/ and you should see a hit counter.

To make this cacheable, we need to add an ETag header to the response. Let's
suppose we only want the image to be cached for up to seven hits. We would
start off by defining a method that generates an ETag to reflect this:

.. testcode::

        def hitcounter_etag(self, request):
                return self.current_count / 7

Then we can use the ``pesto.caching.with_etag`` decorator to apply this to the
counter function, and the ``pesto.caching.etag_middleware`` to make the
application return a ``304 Not Modified`` response when the ETag matches. I
have also put the image generation into a separate function so that it is
lazily generated – the image will not be regenerated when the ETag is matched:

.. testcode::

        import Image
        import ImageDraw
        from StringIO import StringIO
        from pesto import to_wsgi
        from pesto.response import Response
        from pesto.caching import with_etag, etag_middleware

        class HitCounter(object):

                current_count = 0

                def hitcounter_etag(self, request):
                    return self.current_count / 7

                @with_etag(hitcounter_etag, weak=True)
                def counter(self, request):

                        self.current_count += 1

                        def image():
                                yield ''
                                img = Image.new('RGB', (50, 30))
                                draw = ImageDraw.Draw(img)
                                draw.text((10, 10), str(self.current_count))
                                buf = StringIO()
                                img.save(buf, 'PNG')
                                yield buf.getvalue()

                        return Response(image(), content_type='image/png')

        if __name__ == '__main__':
                from wsgiref.simple_server import make_server
                counter = HitCounter()
                app = to_wsgi(counter.counter)
                app = etag_middleware(app)
                httpd = make_server('', 8000, app)
                print "Now load http://localhost:8000/ in a web browser"
                httpd.serve_forever()


.. testcode::
        :hide:

        counter = HitCounter()
        app = to_wsgi(counter.counter)
        app = etag_middleware(app)
        print TestApp(app).get().text().decode('ascii', 'ignore')


Load this in your browser, and examine the headers using the LiveHTTPHeaders
FireFox extension or something similar. You will see an ETag header has been
added:

.. testoutput::

        200 OK
        Content-Type: image/png
        ETag: W/"0"
        ...

Refresh a few times and you should see the server sending a ``304 Not
Modified`` response to repeated requests.

More on ETag generation
````````````````````````

The function ``pesto.caching.with_etag`` expects to be passed a function which must return an object to be used as an ETag. It then uses the following rules:

        * If passed an numeric value or short string, it is used as-is.

        * If passed a long string, an MD5 signature is computed and used as the
          ETag.

        * If passed any other object, the object is pickled and the MD5
          signature of the pickle used as the ETag.

The ``pesto.caching.etag_middleware`` will call the WSGI handler in order to
allow it to set the ``ETag`` header function, and then either abort the
response and return a ``304 Not Modified`` status or proceed with the response.

If the underlying application is a pesto handler, this means the handler will
be invoked and the first iteration of the content iterator called (ie as far as
the first ``yield`` statement in the ``image`` function above), before the content
iterator is closed.

For best performance a good pattern for handlers is:

        * return an generator function to generate the response lazily
        * start that function with ``yield ''``.

For example this is bad: ``very_expensive_calculation`` will be called
every time, even on ETag matches:

.. testcode::

        from pesto.caching import with_etag, etag_middleware
        from pesto.response import Response
        from pesto import to_wsgi

        def very_expensive_calculation():
                print "Calculating!"
                return "The answer is 42"

        @to_wsgi
        @with_etag(lambda request: 'foo')
        def my_handler(request):
                return Response([very_expensive_calculation()])

        app = etag_middleware(my_handler)

We can see that ``very_expensive_calculation`` is called every time by calling this in a test rig:

.. doctest::

        >>> from pesto.testing import TestApp
        >>> print TestApp(app).get('/').text()
        Calculating!
        200 OK
        Content-Type: text/html; charset=UTF-8
        ETag: "foo"
        <BLANKLINE>
        The answer is 42

        >>> print TestApp(app).get('/', HTTP_IF_NONE_MATCH='"foo"').text()
        Calculating!
        304 Not Modified
        Content-Type: text/html; charset=UTF-8
        ETag: "foo"
        <BLANKLINE>
        <BLANKLINE>


Now we rewrite this so that ``very_expensive_calculation`` will be only be
called when the ETag does not match:

.. testcode::

        @to_wsgi
        @with_etag(lambda request: 'foo')
        def my_handler(request):
                def generate_content():
                        yield ''
                        yield very_expensive_calculation()
                return Response(generate_content())

        app = etag_middleware(my_handler)

And we can see that ``very_expensive_calculation`` is not called when we supply
the ``If-None-Match`` header:

.. doctest::

        >>> print TestApp(app).get('/', HTTP_IF_NONE_MATCH='"foo"').text()
        304 Not Modified
        Content-Type: text/html; charset=UTF-8
        ETag: "foo"
        <BLANKLINE>
        <BLANKLINE>

Caching module API documentation
----------------------------------

.. automodule:: pesto.caching
        :members:
