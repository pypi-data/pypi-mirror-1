.. contents:: Contents

Getting started with pesto
##########################

Introduction
=============

This guide covers:

    - downloading and installing the pesto library
    - integrating with a CGI webserver, or using a standalone WSGI server.
    - integrating with a templating system

Installation
=============

Prerequisites
```````````````````

You will need:

    - Python 2.3, 2.4 or 2.5 (recommended)

    - Optionally, the Apache HTTP server with CGI enabled.

    - To run later examples, you will also need the proxy and rewrite modules
      loaded into your apache configuration.

Installing Pesto
```````````````````

Download and install the latest version from `<http://pesto.googlecode.com/>`_, or from the Python Package Index::

    % easy_install pesto

Installing the development version
````````````````````````````````````

For the cutting edge, fetch the development version of pesto from its darcs
repository::

    % darcs get http://darcs.redgecko.org/pesto
    % cd pesto
    % sudo python setup.py install

Using with CGI
==============================

This is the simplest method of integration, but also the most limited and gives the worst performance.

Assuming your web server is already configured to run CGI scripts and pesto is installed you can follow these steps to create a simple pesto web application.

 - Create a CGI script as follows::

    #!/usr/bin/env python

    import pesto
    from pesto import Response

    def handler(request):
        return Response("Welcome to pesto!")

    if __name__ == "__main__":
        app = pesto.to_wsgi(handler)
        pesto.run_with_cgi(app)


 - Save this file in your web server's cgi-bin directory with a name ending in ``.cgi`` (eg ``pesto_test.cgi``).

 - Make sure the permissions are set to allow the script to run (eg ``chmod 755 pesto_test.cgi``)

 - Visit the script with a web browser and if all is well you should see the "Welcome to pesto!" message.


CGI with mod_rewrite
```````````````````````````

If you are using apache and mod_rewrite is enabled, then using a
``RewriteRule`` in your server configuration or from a ``.htaccess`` file is an
easy way of invoking CGI scripts containing multiple handlers.

The following example shows how to set up handlers responding to the URIs
``/pages/one`` and ``/pages/two``. 

**.htaccess** ::

    RewriteEngine On
    RewriteBase /
    RewriteRule ^(pages/?.*) cgi-bin/pesto_test.cgi/$1

**cgi-bin/pesto_test.cgi**::

    #!/usr/bin/python

    import pesto
    import pesto.wsgiutils
    from pesto import Response

    dispatcher = pesto.urldispatcher()

    @dispatcher.match('/page/one', 'GET')
    def render_page(request, response):
        return Response(["This is page one"])

    @dispatcher.match('/page/two', 'GET')
    def render_page(request):
        return Response(["This is page two"])

    if __name__ == "__main__":
        app = pesto.wsgiutils.use_redirect_url()(dispatcher)
        pesto.run_with_cgi(app)

**NB The first time you try this, it is worth enabling debugging in the
dispatcher, as this will log details of the URL processing.** To do this,
change the first 7 lines of your script to the following::

    #!/usr/bin/python

    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    import pesto
    import pesto.wsgiutils
    from pesto import Response

    dispatcher = pesto.urldispatcher(debug=True)



Using a standalone WSGI server
===============================================================

Pesto creates WSGI compatible applications. This means you
can use it to run a pesto based web application under any WSGI server. If you have Python 2.5 or above, you can use the `wsgiref module <http http://docs.python.org/library/wsgiref.html#module-wsgiref>`_:

Let's create two modules, one will contain the handlers and the other to create the WSGI application and run the server. First, create a file called ``myhandlers.py``::

    import pesto
    import pesto.wsgiutils
    dispatcher = pesto.urldispatcher()

    @dispatcher.match('/page/one', 'GET')
    def page_one(request):
        return Response([
            'This is page one. <a href="">Click here for page two</a>...' % page_two.url()
        ])

    @dispatcher.match('/page/two', 'GET')
    def page_two(request):
        return Response([
            '...and this is page two. <a href="">Click here for page one</a>' % page_one.url()
        ])

And a file called ``myapp.py``::

    import myhandlers

    if __name__ == "__main__":
        print "Serving application on port 8000..."
        httpd = make_server('', 8080, myhandlers.dispatcher)
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

Let's assume that you want to run a site at the location http://localhost:80/.

Apache will listen on port 80, and the python webserver will listen on port
8080. You'll need to install the Paste modules as detailed above if you haven't
already done so.

In your httpd.conf, set up the following directives::

        RewriteEngine On
        RewriteRule ^/(.*)$ http://localhost:8080/$1 [L,P]
        ProxyVia On

The first ``RewriteRule`` simply proxies everything to the WSGI server.

Restart apache and visit http://localhost/page/one - you should see a ``Bad
Gateway`` error page. Don't panic - this means that the proxying is working in
apache, but your application is not running yet.

Modify ``myapp.py`` to read as follows::

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
investigate the `Paste <http://pythonpaste.org>` package.

HTTPS
```````

For URI generation to work correctly when proxying from an Apache/mod_ssl
server, you will need to add the following to the Apache configuration in the
SSL `<virtualhost>` section::

    RequestHeader set X_FORWARDED_SSL 'ON'


Basic concepts
==============

Sample application
```````````````````

Here's a simple web application giving an overview of the functions provided
by pesto. To run this, copy this code into a file called ``recipes.py`` and run
the file by typing ``python recipes.py``:: 

    #!/usr/bin/python

    from wsgiref import simple_server

    import pesto
    from pesto import Response
    dispatcher = pesto.urldispatcher()

    recipes = {
        'baked-beans' : "Open a tin of baked beans. Put into a saucepan, heat and serve.",
        'toast'       : "Put a slice of bread under a grill for 2-3 minutes, turning once. Serve.",
    }

    @dispatcher.match('/', 'GET')
    def recipe_index(request):
        """
        Display an index of available recipes.
        """

        return Response(
            ['<html><body><h1>List of recipes</h1><ul>']
            + [ '<li><a href="%s">%s</a></li>' % (show_recipe.url(recipe=r), r) for r in recipes ]
            + ['</ul></body></html>']
        )

    @dispatcher.match('/recipes/<recipe:unicode>', 'GET')
    def show_recipe(request, recipe):
        """
        Display a single recipe
        """
        return [
            '<html><body><h1>How to make %s</h1>' % recipe,
            '<p>%s</p><a href="%s">Back to index</a>' % (recipes[recipe], recipe_index.url()),
            '</body></html>'
        ]

    if __name__ == "__main__":
        app = dispatcher
        httpd = simple_server.make_server('', 8080, app)
        httpd.serve_forever()


Pesto handlers
```````````````````

Pesto handlers are at the heart of the pesto library. The basic signature of a handler is::

    def my_handler(request):
        return Response(["<h1>Whoa Nelly!</h1>"])

Handlers must accept a request object and must return a ``pesto.response.Response`` object.
The ``Response`` object should contain an iterable payload. In the example
above the payload is HTML, but any data can be returned. For example, the
following are all valid Response objects::

    # Simple textual response
    return Response(['ok'])

    # Efficient iterator over a data file
    with open('data.gif', 'r') as img:
        return Response(
            iter(partial(img.read, 8192), None),
            content_type = 'image/gif'
        )

    # Iterator over database query
    def format_results(cursor):
        for row in iter(cursor.fetchone, None):
            yield '<tr><th>%s</th><td>%d</td></tr>' % row
    return Response(format_results(cursor))

Function decorators
```````````````````

Pesto works really well with function decorators. Here's
a couple of examples of the sort of thing that are easy to do.

First up, a decorator to set caching headers on the response::

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

Usage::

    @nocache
    def handler(request):
        return Response(['blah'])


Second: a decorator to allow handlers to return datastructures which are
automatically converted into JSON notation (requires SimpleJSON)::

    def json(func):

        """
        Wrap a pesto handler to return a JSON-encoded string from a python
        data structure.
        """
        import simplejson

        @wraps(func)
        def json(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if isinstance(result, Response):
                return result
            return Response(
                content=[simplejson.dumps(result)],
                content_type='application/json'
            )

        json.__name__ = func.__name__
        return json

Finally, a decorator to turn 'water' into 'wine'::

    def water2wine(func):
        @wraps(func)
        def water2wine(*args, **kwargs):
            res = func(*args, **kwargs)
            return res.replace(
                content=(chunk.replace('water', 'wine') for chunk in res.content)
            )
        return miracle

These decorators are all used the same way and may be chained together. For
example::

    @dispatch.match('/get-drink-preference')
    @water2wine
    @nocache
    @json
    def handler(request):
        return {'preferred-drink': 'water' }


Running pesto applications
`````````````````````````````````````

Pesto and WSGI
'''''''''''''''

The ``to_wsgi`` utility function transforms a pesto handler function into a
WSGI application. This can then be run by any WSGI compliant server, eg
`wsgiref.simple_server <http://docs.python.org/lib/module-wsgiref.simpleserver.html>`_, or in a CGI
environment by using ``pesto.run_with_cgi``::

    app = pesto.to_wsgi(my_handler)
    pesto.run_with_cgi(app)

Pesto ``urldispatcher`` instances are also WSGI applications. So to complete
the recipe example above and create an application that will run under a CGI
server (eg Apache) we can add the following few lines of code::


    dispatcher = pesto.urldispatcher()
    dispatcher.match('/recipes', GET=handlers.recipe_index)
    dispatcher.match('/recipes/<recipe_id:int>', GET=handlers.show_recipe)
    dispatcher.match('/recipes/<recipe_id:int>/edit',
        GET=handlers.edit_recipe_form,
        POST=handlers.edit_recipe_save
    )
    pesto.run_with_cgi(dispatcher)


Using pesto with a templating system
=====================================

Unlike many frameworks, Pesto does not tie you to any particular templating
system. As an example of how you can use a templating system in your
application, here is a minimal example of code that uses the `Genshi
<http://genshi.edgewall.org/>`_ templating library::

    import os

    from genshi.template.loader import TemplateLoader

    import pesto
    from pesto import Response

    template_path = os.path.abspath('./templates')
    templateloader = TemplateLoader([template_path])

    def render_template(filepath, **kwargs):
        """
        Render an XHTML template in genshi, passing any keyword arguments to
        the template namespace.
        """
        template = templateloader.load(filepath)

        for chunk in template.generate(**kwargs).serialize(method='xhtml'):
            yield unicode(chunk).encode('utf8')

    def homepage(request):
        return = Response(template("homepage.html"))

    def app_factory(global_cfg, **kwargs):
        """
        Create a new WSGI application
        """
        return pesto.to_wsgi(homepage)

    if __name__ == "__main__":
        pesto.run_with_cgi(app_factory({}))




