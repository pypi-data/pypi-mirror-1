.. testsetup:: *

        from pesto.response import Response
        from pesto import to_wsgi
        from pesto.testing import TestApp


Getting started with Pesto
##########################

.. contents:: Contents

Introduction
=============

This guide covers:

    - Downloading and installing the Pesto library
    - Running applications with an existing web server or a standalone WSGI
      server.
    - Integrating applications with a templating system

Installation
=============

Pesto requires Python 2.4, 2.5 or 2.6 (recommended) with `setuptools
<http://peak.telecommunity.com/DevCenter/setuptools>`_

You will need a webserver to run the examples. There are examples in this guide
for integrating with a CGI webserver (eg Apache), or using a WSGI server which
can either run standalone or be integrated with a front end server such as
Apache.


Installing Pesto
```````````````````

Download and install the latest version from the Python Package Index::

    % easy_install pesto

Installing the development version
````````````````````````````````````

For the cutting edge, fetch the development version of Pesto from its darcs
repository::

    % darcs get http://patch-tag.com/r/pesto/pullrepo pesto
    % cd pesto
    % sudo python setup.py install

Programming with Pesto: basic concepts
======================================

Pesto provides:

        - A request object that gives you easy access to information about the
          request, eg the URL and any submitted form data.

        - A response class that makes it easy to construct HTTP responses.

        - A URI dispatch mechanism to help you map URIs to handler functions.

        - Functions that convert your handler functions to WSGI functions, and
          back again.

Sample application
```````````````````

Here's a simple web application giving an overview of the functions provided
by Pesto. Save this code in a file called ``guestbook.py``:

.. testcode::

        #!/usr/bin/python

        from wsgiref import simple_server
        from cgi import escape
        from datetime import datetime

        from pesto import Response, dispatcher_app
        dispatcher = dispatcher_app()

        entries = [] 

        @dispatcher.match('/', 'GET')
        def guestbook(request):
                """
                Display an index of all entries
                """
                content = [
                        '<html><body><h1>Welcome to my Guestbook</h1>'
                        '<form method="POST" action="%s">'
                        'Name: <input type="text" name="name"/><br/>'
                        'Your message: <textarea name="message"></textarea><br/>'
                        '<input type="submit" value="Add message"/>'
                        '</form>' % add_entry.url()
                        ]
                content.extend([
                        '<h2>From %s @ %s</h2><p>%s</p><a href="%s">view details</a>' % (
                                escape(entry['name']),
                                entry['date'].strftime('%d/%m/%Y %H:%M'),
                                escape(entry['message']),
                                view_entry.url(index=ix),
                        ) for ix, entry in reversed(list(enumerate(entries)))
                ])
                return Response(content)

        @dispatcher.match('/add-entry', 'POST')
        def add_entry(request):
                """
                Add an entry to the guestbook then redirect back to the main
                guestbook page.
                """
                entries.append({
                        'date': datetime.now(),
                        'name': request.form.get('name', ''),
                        'message': request.form.get('message', ''),
                        'ip': request.remote_addr,
                        'useragent': request.get_header('User-Agent', ''),
                })
                return Response.redirect(guestbook.url())

        @dispatcher.match('/view-entry/<index:int>', 'GET')
        def view_entry(request, index):
                """
                View all details of an individual entry
                """
                try:
                        entry = entries[index]
                except IndexError:
                        return Response.not_found()

                return Response(["""
                        <html><body>
                        <table>
                        <tr><th>Name</th><td>%s</td></tr>
                        <tr><th>Time</th><td>%s</td></tr>
                        <tr><th>IP address</th><td>%s</td></tr>
                        <tr><th>Browser</th><td>%s</td></tr>
                        <tr><th>Message</th><td>%s</td></tr>
                        </table>
                        <a href="%s">Back</a>""" % (
                                escape(entry['name']),
                                entry['date'].strftime('%d %m %Y %H:%M'),
                                escape(entry['ip']),
                                escape(entry['useragent']),
                                escape(entry['message']),
                                guestbook.url()
                        )
                ])

        if __name__ == "__main__":
                httpd = simple_server.make_server('', 8080, dispatcher)
                httpd.serve_forever()

.. doctest::
        :hide:

        >>> app = TestApp(dispatcher)
        >>> '<h1>Welcome to my Guestbook</h1>' in app.get('/').body
        True
        >>> print app.post('/add-entry', data={'name': 'Jim', 'message': "hello, I'm Jim & I like guestbooks"}).text()
        302 Found
        ...
        Location: http://localhost/
        ...
        >>> "hello, I'm Jim &amp; I like guestbooks" in app.get('/').body
        True
        >>> print app.get('/view-entry/2').text()
        404 Not Found
        ...
        >>> print app.get('/view-entry/0').text()
        200 OK
        ...
                        <tr><th>Name</th><td>Jim</td></tr>
                        <tr><th>Time</th><td>...</td></tr>
                        <tr><th>IP address</th><td>127.0.0.1</td></tr>
                        <tr><th>Browser</th><td></td></tr>
                        <tr><th>Message</th><td>hello, I'm Jim &amp; I like guestbooks</td></tr>
        ...


Run the file by typing ``python guestbook.py`` and a web server should start on port 8080.

Here's a line-by-line breakdown of the important functionality illustrated
here:

--------

::

        dispatcher = dispatcher_app()

``pesto.dispatcher_app`` is a WSGI application that takes incoming requests
and routes them to handler functions. In their simplest form, handler functions
take a single argument (a ``pesto.request.Request`` object) and must return a
``pesto.response.Response`` object.

--------

::

        @dispatcher.match('/', 'GET')
        def guestbook(request):
                ...

        @dispatcher.match('/add-entry', 'POST')
        def add_entry(request):
                ...

Using ``@dispatcher.match`` is the most convenient way to match URIs to handler
functions. You need to specify both the path and at least one HTTP method
(usually ``GET`` or ``POST``). 

In this case, the function ``guestbook`` will be called for all GET requests to
``http://<your-server>/``, while ``add_entry`` will be called for POST requests
to ``http://<your-server/add-entry``.

--------

::

                content = [
                        '<html><body><h1>Welcome to my Guestbook</h1>'
                        ...
                ]
                ...
                return Response(content)

The ``Response`` object returned by a handler function specifies the response
body and any HTTP headers. ``Response`` requires one argument, which must be an
iterator over the content you want to return. Other arguments can be used to
specify HTTP headers and other aspects of the response.
If you don't tell Pesto otherwise it will assume that the HTTP status should be
``200 OK`` and that the content type should be ``text/html; charset=UTF-8``.

--------

::

                return Response.redirect(guestbook.url())

``Response.redirect`` is a method that returns a 302 redirect to the web
browser to any given URL. Because the ``guestbook`` has been mapped to a URL
via the ``pesto.dispatcher_app`` class, we can call ``guestbook.url()`` to
retrieve the fully qualified URL pointing to that function.

--------

::

        @dispatcher.match('/view-entry/<index:int>', 'GET')
        def view_entry(request, index):
                """
                View all details of an individual entry
                """

Again we are using the dispatcher object to map a URI to a function. Here we
want to extract the second part of the URI and pass it as the named argument
``index`` to the function. We also tell Pesto that it should convert the value
to an integer. Other pattern types are supported, like ``<name:unicode>`` or
``<flavour:any('vanilla', 'mango', 'grape')>``. You can also define your own
pattern matching rules.

--------

::

                try:
                        entry = entries[index]
                except IndexError:
                        return Response.not_found()

The ``Response`` class contains predefined functions for most error responses.
Returning ``Response.not_found`` will automatically return a 404 response to
the web browser.

Using with CGI
==============================


If you have access to a web server that is already configured to run CGI scripts and then
this is a quick way to get started with Pesto. However it is more limited that
other methods and can give poor performance.

Let's start by creating a CGI script as follows:

.. testcode::

        #!/usr/bin/env python

        import pesto
        from pesto import Response

        def handler(request):
                return Response(["Welcome to Pesto!"])

        if __name__ == "__main__":
                app = pesto.to_wsgi(handler)
                pesto.run_with_cgi(app)


Save this file in your web server's cgi-bin directory with the filename
``pesto_test.cgi``

Visit the script with a web browser and if all is well you should see the "Welcome to Pesto!" message.

If you don't see this message, check that the file permissions are set correctly
(ie ``chmod 755 pesto_test.cgi``). You may also need to change the first line
of your script to read either ``#!/usr/bin/python`` or
``#!/usr/local/bin/python``, depending on your hosting provider.

CGI with mod_rewrite
```````````````````````````

If you are using Apache and mod_rewrite is enabled, then using a
``RewriteRule`` in your server configuration or from a ``.htaccess`` file is an
easy way of running CGI scripts that gives you user friendly URIs and the
possibility of having more than one handler function per script.

Here is how to set up a script that responds to the URIs ``/pages/one`` and
``/pages/two``. 

**.htaccess**

::

    RewriteEngine On
    RewriteBase /
    RewriteRule ^(pages/.*) cgi-bin/pesto_test.cgi/$1

**cgi-bin/pesto_test.cgi**

.. testcode::

    #!/usr/bin/python

    import pesto
    import pesto.wsgiutils
    from pesto import Response

    dispatcher = pesto.dispatcher_app()

    @dispatcher.match('/page/one', 'GET')
    def render_page(request, response):
        return Response(["This is page one"])

    @dispatcher.match('/page/two', 'GET')
    def render_page(request):
        return Response(["This is page two"])

    if __name__ == "__main__":
        app = pesto.wsgiutils.use_redirect_url()(dispatcher)
        pesto.run_with_cgi(app)

The first time you try this, you might want to enable debugging in the
dispatcher to log details of the URL processing. To do this, change the first
7 lines of your script to the following:

::

    #!/usr/bin/python

    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    import pesto
    import pesto.wsgiutils
    from pesto import Response

    dispatcher = pesto.dispatcher_app(debug=True)



Using a standalone WSGI server
===============================================================

You can run a Pesto based web application under any WSGI server. If you have
Python 2.5 or above, you can use the `wsgiref module
<http://docs.python.org/library/wsgiref.html#module-wsgiref>`_ from the Python
standard library.

First, create a file called ``myhandlers.py``:

.. testcode::

    import pesto
    import pesto.wsgiutils
    dispatcher = pesto.dispatcher_app()

    @dispatcher.match('/page/one', 'GET')
    def page_one(request):
        return Response([
            'This is page one. <a href="%s">Click here for page two</a>...' % (page_two.url(),)
        ])

    @dispatcher.match('/page/two', 'GET')
    def page_two(request):
        return Response([
            '...and this is page two. <a href="%s">Click here for page one</a>' % (page_one.url(),)
        ])

.. doctest::
        :hide:

        >>> TestApp(dispatcher).get('/page/one').body
        'This is page one. <a href="http://localhost/page/two">Click here for page two</a>...'
        >>> TestApp(dispatcher).get('/page/two').body
        '...and this is page two. <a href="http://localhost/page/one">Click here for page one</a>'

And a file called ``myapp.py``:

::

        import myhandlers

        if __name__ == "__main__":
                print "Serving application on port 8000..."
                httpd = make_server('', 8080, dispatcher)
                httpd.serve_forever()

Now you can start the server by running myapp.py directly::

    % python myapp.py
    Serving application on port 8080...

Visit http://localhost:8080/page/one in your web browser and see the
application in action.

Virtualhosting and Apache
==========================

Using a standalone webserver has many advantages. But it's better if
you can proxy it through another web server such as Apache. This gives added
flexibility and security and if necessary, you can set up proxy caching to get
a big performance boost.

**For the following to work, you need to make sure your apache installation has
the proxy and rewrite modules loaded.** Refer to the 
`Apache HTTP server documentation <http://httpd.apache.org/docs/>`_ for details of
how to achieve this.

Let's assume that you want to run a site at the URL http://example.com/. For
this configuration we need Apache to listen on port 80, and the WSGI server on
any other port – we'll use port 8080 in this example.

In your httpd.conf, set up the following directives::

        RewriteEngine On
        RewriteRule ^/(.*)$ http://localhost:8080/$1 [L,P]
        ProxyVia On

The first ``RewriteRule`` simply proxies everything to the WSGI server.

Restart apache and visit http://localhost/page/one - you should see a ``Bad
Gateway`` error page. Don't panic – this means that the proxying is working in
apache, but your application is not running yet.

Modify ``myapp.py`` to read as follows:

::

        import myhandlers
        import pesto.wsgiutils

        def make_app():
                app = myhandlers.dispatcher
                app = pesto.wsgiutils.use_x_forwarded()(app)
                return app

        if __name__ == "__main__":
                print "Serving application on port 8000..."
                httpd = make_server('', 8080, make_app())
                httpd.serve_forever()

To see it in action, fire up the server::

    % python myapp.py
    Serving application on port 8080...

and reload http://localhost/page/one in your browser: you should now see your
pesto application being server through Apache.

For a more sophisticated setup suitable for production applications, you should
investigate the `Paste <http://pythonpaste.org>`_ package.

HTTPS
```````

For URI generation to work correctly when proxying from an Apache/mod_ssl
server, you will need to add the following to the Apache configuration in the
SSL `<virtualhost>` section::

    RequestHeader set X_FORWARDED_SSL 'ON'



Pesto handlers
```````````````````

Pesto handlers are at the heart of the Pesto library. The basic signature of a handler is:

.. testcode::

    def my_handler(request):
        return Response(["<h1>Whoa Nelly!</h1>"])

Handlers must accept a request object and must return a ``pesto.response.Response`` object.
The ``Response`` constructor takes at least one argument, ``content``, which
must be an iterator over the content you want to return.

In the example above the payload is HTML, but any data can be returned. For
example, the following are also examples of valid Response objects:

.. testcode::
        :hide:

        cursor = None

.. testcode::

        # Simple textual response
        Response(['ok'], content_type="text/plain")

        # Iterator over database query
        def format_results(cursor):
                yield "<table>"
                for row in iter(cursor.fetchone, None):
                        yield '<tr>'
                        for column in row:
                                yield '<td>%d</td>' % column
                        yield '</tr>'
                yield "</table>"
        Response(format_results(cursor))


Function decorators
```````````````````

Function decorators are simple, expressive and a natural way to add
functionality to web applications using Pesto. Here are a few examples.

First up, a decorator to set caching headers on the response:

.. testcode::

        from functools import wraps
        
        def nocache(func):
            """
            Pesto middleware to send no-cache headers.
            """
            @wraps(func)
            def nocache(request, *args, **kwargs):
                res = func(request, *args, **kwargs)
                res = res.add_header("Cache-Control", "no-cache, no-store, must-revalidate")
                res = res.add_header("Expires", "Mon, 26 Jul 1997 05:00:00 GMT")
                return res
            return nocache

This could be used as follows:

.. testcode::

        @nocache
        def handler(request):
            return Response(['blah'])

.. testcode::
        :hide:

        from pesto.testing import TestApp
        print TestApp(to_wsgi(handler)).get('/').text()

Giving the following output:

.. testoutput::

        200 OK
        Cache-Control: no-cache, no-store, must-revalidate
        Content-Type: text/html; charset=UTF-8
        Expires: Mon, 26 Jul 1997 05:00:00 GMT

        blah


Second: a decorator to allow handlers to return datastructures which are
automatically converted into JSON notation (this example requires python 2.6,
for earlier versions you will need to install the SimpleJSON module installed):

.. testcode::

        import json

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

Finally, a decorator to turn 'water' into 'wine':

.. testcode::

        def water2wine(func):
            @wraps(func)
            def water2wine(*args, **kwargs):
                res = func(*args, **kwargs)
                return res.replace(
                    content=(chunk.replace('water', 'wine') for chunk in res.content)
                )
            return water2wine

Decorators may be chained together, for example:

.. testcode::

        from pesto import dispatcher_app
        dispatcher = dispatcher_app()
        @dispatcher.match('/drink-preference', 'GET')
        @water2wine
        @nocache
        @to_json
        def handler(request):
            return {'preferred-drink': 'water' }

.. testcode::
        :hide:

        from pesto.testing import TestApp
        print TestApp(dispatcher).get('/drink-preference').text()

This would output the following JSON response:

.. testoutput::

        200 OK
        Cache-Control: no-cache, no-store, must-revalidate
        Content-Type: application/json
        Expires: Mon, 26 Jul 1997 05:00:00 GMT

        {"preferred-drink": "wine"}


Running Pesto applications
`````````````````````````````````````

Pesto and WSGI
'''''''''''''''

The ``to_wsgi`` utility function adapts a Pesto handler function to form a WSGI
application. This can then be run by any WSGI compliant server, eg
`wsgiref.simple_server <http://docs.python.org/lib/module-wsgiref.simpleserver.html>`_::

        from wsgiref.simpleserver import make_server
        app = pesto.to_wsgi(my_handler)
        httpd = make_server('', 8000, app)
        print "Serving on port 8000..."
        httpd.serve_forever()

Or in a CGI environment (eg for shared hosting) by using ``pesto.run_with_cgi``::

    app = pesto.to_wsgi(my_handler)
    pesto.run_with_cgi(app)

Pesto ``dispatcher_app`` instances are WSGI applications and can be passed
directly to ``pesto.run_with_cgi``.



Using Pesto with a templating system
=====================================

Unlike many frameworks, Pesto does not tie you to any particular templating
system. As an example of how you can use a templating system in your
application, here is a minimal example of code that uses the `Genshi
<http://genshi.edgewall.org/>`_ templating library:

.. testcode::

        import os
        from functools import wraps
        from genshi.template.loader import TemplateLoader
        import pesto
        from pesto import Response


        templateloader = TemplateLoader(["."])
        def render(filepath):
                """
                Render a template in genshi, passing any keyword arguments to the
                template namespace.
                """
                def decorator(func):
                        @wraps(func)
                        def decorated(request, *args, **kwargs):
                                template = templateloader.load(filepath)
                                data = func(request, *args, **kwargs)
                                return Response([
                                        template.generate(
                                                **data
                                        ).render(method='xhtml', encoding='utf8')
                                ])
                        return decorated
                return decorator

        dispatcher = pesto.dispatcher_app(debug=True)

        @dispatcher.match("/<name:unicode>", "GET")
        @render("welcome.html")
        def welcome(request, name):
                return {'name': name.title()}

        if __name__ == "__main__":
                from wsgiref.simpleserver import make_server
                print "Serving application on port 8000..."
                httpd = make_server('', 8080, d)
                httpd.serve_forever()


To make this work, we'll need a template file:

.. doctest::

        >>> f = open('welcome.html', 'w')
        >>> f.write('''
        ... <html>
        ...   <body>
        ...     <h1>Greetings, $name!</h1>
        ...   </body>
        ... </html>
        ... ''')
        >>> f.close()

.. testcode::
        :hide:

        print TestApp(dispatcher).get('/fred').body

Once running, a call to ``http://localhost:8080/fred`` should give you the following result:

.. testoutput::

        <html>
          <body>
            <h1>Greetings, Fred!</h1>
          </body>
        </html>

