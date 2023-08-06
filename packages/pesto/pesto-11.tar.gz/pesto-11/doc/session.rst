Session storage
===============

Example::

    @dispatcher.match('/login', 'POST')
    def login(request):

        username = request.get('username')
        password = request.get('password')

        if is_valid(username, password):
            request.session['username'] = username
            request.session['logged_in'] = True

        ...

    @dispatcher.match('/secure-area', 'GET')
    def secure_area(request):

        if not request.session.get('logged_in'):
            return response.redirect(login.url())

        return ["Welcome to the secure area, %s" % request.session['username']]

    ...

    from pesto.session.memorysessionmanager import MemorySessionManager

    # Create a memory based sessioning middleware, that runs a purge every 600s
    # for sessions older than 1800s..
    sessioning = pesto.session_middleware(
        MemorySessionManager(),
        auto_purge_every=600,
        auto_purge_olderthan=1800
    )

    application = dispatcher
    application = sessioning(application)

Sessioning needs some kind of storage backend. The two primary backends are memory and file backed storage.

Memory backend
----------------

Synopsis::

    from pesto.session.memorysessionmanager import MemorySessionManager
    app = pesto.session_middleware(MemorySessionManager())(app)

This is the fastest implementation, but only suitable for applications running
in a single process persistent environment (eg not CGI).

File backed
-----------

This backend is the most suitable for CGI or other non-persistent environments.

Synopsis::

    from pesto.session.filesessionmanager import FileSessionManager
    session_manager = FileSessionManager('/tmp/sessions')
    app = pesto.session_middleware(session_manager)(app)

.. automodule:: pesto.session.base
        :members:

.. automodule:: pesto.session.memorysessionmanager
        :members:

.. automodule:: pesto.session.filesessionmanager
        :members:
