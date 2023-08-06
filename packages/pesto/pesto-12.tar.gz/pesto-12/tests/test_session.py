# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

import re
import time

from nose.tools import assert_equal

import pesto
from pesto.response import Response
from pesto.core import to_wsgi
from pesto.testing import TestApp
from pesto.session.base import ID_LENGTH
from pesto.session.memorysessionmanager import MemorySessionManager

def get_session_id(response):
    cookie = response.get_header('Set-Cookie')
    if cookie:
        return re.match('pesto_session=([\w\d]+);', cookie).group(1)
    return None

def test_cookie():

    sessionmanager = MemorySessionManager(cache_size=10)

    @to_wsgi
    def app(request):
        return Response(['ok'])

    response = TestApp(
        pesto.session_middleware(
            sessionmanager,
            auto_purge_every=0,
        )(app)
    ).get('/')


    # Check we got a session id back
    session_id = get_session_id(response)
    assert len(session_id) == ID_LENGTH


def test_persistence():

    @to_wsgi
    def app(request):
        request.session['counter'] = request.session.get('counter', -1) + 1
        return Response()

    sessionmanager = MemorySessionManager(cache_size=10)
    app = pesto.session_middleware(sessionmanager)(app)

    app = TestApp(app)
    response = app.get('/')

    # Check we get a session id back
    session_id = get_session_id(response)
    assert len(session_id) == ID_LENGTH

    # Now, send back the session id we've just got. Check that we get the same
    # session back each time and that the session counter is incrementing

    for ix in range(10):

        response = app.get(
            '/',
            HTTP_COOKIE="pesto_session=" + session_id
        )
        assert_equal(sessionmanager.load(session_id)['counter'], ix + 1) # Add one for initial run

def test_persistence_qs():

    @to_wsgi
    def app(request):
        request.session['counter'] = request.session.get('counter', -1) + 1
        return Response()

    sessionmanager = MemorySessionManager(cache_size=10, persist='querystring')
    app = TestApp(pesto.session_middleware(sessionmanager)(app))

    response = app.get('/')
    assert_equal(response.status, '302 Found')
    uri = response.get_header('Location')
    from urlparse import urlparse
    uri = urlparse(uri)
    assert 'pesto_session' in uri.query
    response = app.get(uri.path, QUERY_STRING=uri.query)

    # Check we get a session id back
    session_id = re.search('pesto_session=([\w\d]+)', uri.query).group(1)
    assert_equal(len(session_id), ID_LENGTH)

    # Now, send back the session id we've just got. Check that we get the same
    # session back each time and that the session counter is incrementing

    for ix in range(10):

        assert_equal(app.get(uri.path, QUERY_STRING=uri.query).status, '200 OK')
        assert_equal(sessionmanager.load(session_id)['counter'], ix + 1) # Add one for initial run


def test_is_new():

    sessionmanager = MemorySessionManager(cache_size=10)

    @to_wsgi
    def first_app(request):
        assert request.session.is_new
        return Response()

    first_app = pesto.session_middleware(sessionmanager)(first_app)

    @to_wsgi
    def second_app(request):
        assert not request.session.is_new
        return Response()

    second_app = pesto.session_middleware(sessionmanager)(second_app)

    response = TestApp(first_app).get('/')
    session_id = get_session_id(response)

    response = TestApp(second_app).get(
        '/', HTTP_COOKIE="pesto_session=" + session_id
    )



def test_expiry():

    sessionmanager = MemorySessionManager(cache_size=10)

    @to_wsgi
    def app(request):
        return Response(['ok'])

    app = pesto.session_middleware(
        sessionmanager,
        auto_purge_every=0.1,
        auto_purge_olderthan=0.2
    )(app)
    app = TestApp(app)


    response = app.get('/')

    session_id = get_session_id(response)
    response = app.get('/', HTTP_COOKIE="pesto_session=" + session_id)

    # Should not have had time to expire (yet) therefore we won't get a cookie
    # back - the original one is still valid.
    assert get_session_id(response) is None

    # Allow time for session to expire
    time.sleep(1)

    response = app.get('/', HTTP_COOKIE="pesto_session=" + session_id)

    # Check we got a new session id back
    assert get_session_id(response) != session_id


def test_cookie_once_only():
    """
    Make sure the session middleware sends back a cookie only when the session
    is created and not on subsequent requests.
    """
    sessionmanager = MemorySessionManager(cache_size=10)

    @to_wsgi
    def app(request):
        return Response(['hello world'])

    app = pesto.session_middleware(sessionmanager)(app)

    app = TestApp(app)
    response = app.get('/')
    assert response.get_header("Set-Cookie")
    session_id = get_session_id(response)

    response = app.get('/', HTTP_COOKIE="pesto_session=" + session_id)
    assert not response.get_header("Set-Cookie")

