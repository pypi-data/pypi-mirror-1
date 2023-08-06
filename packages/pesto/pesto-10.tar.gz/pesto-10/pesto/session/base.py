# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__docformat__ = 'restructuredtext en'
__version__ = '2'
__all__ = ['session_middleware']

"""
Web session management.
"""

import cgi
import cPickle
import logging
import md5
import os
import random
import re
import time
import threading

from pesto.cookie import Cookie, parse_cookie_header
from pesto.wsgiutils import ClosingIterator, StartResponseWrapper

def _get_session_id_from_querystring(environ):
    """
    Return the session from the query string or None if no session can be read.
    """

    query = environ.get("QUERY_STRING", "")
    try:
        return re.match(re.escape(Session.COOKIE_NAME) + '=([0-9a-z]{%d})' % ID_LENGTH).group(0)
    except AttributeError:
        return None

def _get_session_id_from_cookie(environ):
    """
    Return the session from a cookie or None if no session can be read
    """
    if 'pesto.request' in environ:
        cookies = environ['pesto.request'].cookies
    else:
        cookies = parse_cookie_header(environ.get("HTTP_COOKIE"))
    for cookie in cookies:
        if cookie.name == Session.COOKIE_NAME:
            try:
                if is_valid_id(cookie.value):
                    return cookie.value
            except KeyError:
                pass

    return None


try:
    import hashlib
    ID_LENGTH = hashlib.sha256().digest_size * 2
    def generate_id():
        return hashlib.sha256(
              str(os.getpid())
            + str(time.time())
            + str(random.random())
        ).hexdigest()

except ImportError:
    import sha
    ID_LENGTH = 40
    def generate_id():
        return sha.new(
              str(os.getpid())
            + str(time.time())
            + str(random.random())
        ).hexdigest()


def is_valid_id(session_id, pattern=re.compile('^[a-f0-9]{%d}$' % ID_LENGTH)):
    """
    Return True if ``session_id`` is a well formed session id. This must be
    a hex string as produced by hashlib objects' ``hexdigest`` method.

    Synopsis::

        >>> is_valid_id('a' * ID_LENGTH)
        True
        >>> is_valid_id('z' * ID_LENGTH)
        False
        >>> is_valid_id('a' * (ID_LENGTH - 1))
        False
    """
    try:
        return pattern.match(session_id) is not None
    except TypeError:
        return False


class Session(object):
    """
    Session objects store information about the http sessions
    """

    COOKIE_NAME = "pesto_session"
    COOKIE_PATH = "/"

    # Indicates whether the session is newly created (ie within the current request)
    is_new = True

    def __init__(self, session_manager, session_id, is_new, data=None):
        """
        Create a new session object within the given session manager.
        """

        self.session_manager = session_manager
        self._changed = False
        self.session_id = session_id
        self.is_new = is_new
        self.data = {}

        if data is not None:
            self.data.update(data)

    def save(self):
        """
        Save the session in the underlying storage mechanism.

        Note it will only do this if the session is new or has been
        changed since being loaded.

        Return
            ``True`` if the session was saved, or ``False`` if it
            was not necessary to save the session.
        """
        if self._changed or self.is_new:
            self._save()
            self._changed = False
            self.is_new = False
            return True
        return False

    def _save(self):
        """
        Saves the session in the underlying storage mechanism.
        """
        if self.session_id:
            self.session_manager.store(self)

    def setdefault(self, key, value=None):
        self._changed = True
        return self.data.setdefault(key, value)

    def pop(self, key, default):
        self._changed = True
        return self.data.pop(key, default)

    def popitem(self):
        self._changed = True
        return self.data.popitem()

    def clear(self):
        self._changed = True
        return self.data.clear()

    def has_key(self, key):
        return self.data.has_key(key)

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def update(self, other, **kwargs):
        self._changed = True
        return self.data.update(other, **kwargs)

    def values(self):
        return self.data.values()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return self.data.__iter__()

    def invalidate(self, response=None):
        """
        invalidate and remove this session from the sessionmanager
        """
        self.session_manager.remove(self.session_id)
        self.session_id = None

    def __setitem__(self, key, val):
        self._changed = True
        return self.data.__setitem__(key, val)

    def __delitem__(self, key):
        self._changed = True
        return self.data.__delitem__(key)

    def text(self):
        """
        Return a useful text representation of the session
        """
        import pprint
        return "<%s id=%s, is_new=%s\n%s\n>" % (
                self.__class__.__name__, self.session_id, self.is_new,
                pprint.pformat(self)
        )

class SessionManagerBase(object):
    """
    Manages Session objects using an ObjectStore to persist the
    sessions.
    """
    # Which version of the pickling protocol to select.
    PICKLE_PROTOCOL = -1

    def __init__(self, persist='cookie', secret=None):
        """
        persist
            How to persist the session-id: either ``cookie`` or ``querystring`` must be specified
        """
        self._secret = secret
        assert persist in ('cookie', 'querystring')
        self.persist = persist
        if persist == 'cookie':
            self._get_session_id = _get_session_id_from_cookie
        if persist == 'querystring':
            self._get_session_id = _get_session_id_from_querystring

    def load(self, session_id):
        """
        Load a session object from this sessionmanager.

        Note that if ``session_id`` cannot be found in the underlying storage,
        a new session id will be created.
        """
        self.acquire_lock(session_id)
        try:
            is_new = False
            data = self._get_session_data(session_id)

            if data is None:

                # Generate a fresh session with a new id
                session = Session(self, generate_id(), is_new=True, data={})

            else:
                session = Session(self, session_id, is_new=False, data=data)
            self.update_access_time(session_id)
            return session
        finally:
            self.release_lock(session_id)

    def update_access_time(session_id):
        raise NotImplementedError

    def acquire_lock(self, session_id=None):
        """
        Acquire a lock for the given session_id.

        If session_id is none, then the whole storage should be locked.
        """
        raise NotImplementedError

    def release_lock(self, session_id=None):
        raise NotImplementedError

    def read_session(self, environ):
        """
        Attempts to read the session id from the query string or cookies, and
        returns an Session object.

        Synopsis::

            >>> from pesto.session.memorysessionmanager import MemorySessionManager
            >>> sm = MemorySessionManager()
            >>> sm.read_session({}) #doctest: +ELLIPSIS
            <pesto.session.base.Session object at 0x...>

        """

        session_id = self._get_session_id(environ)
        if session_id is not None:
            return self.load(session_id)

        return Session(self, generate_id(), is_new=True)

    def __contains__(self, session_id):
        """
        Return true if the given session id exists in this sessionmanager
        """
        raise NotImplementedError

    def store(self, session):
        """
        Save the given session object in this sessionmanager.
        """
        self.acquire_lock(session.session_id)
        try:
            self._store(session)
        finally:
            self.release_lock(session.session_id)

    def _store(self, session):
        """
        Write session data to the underlying storage.
        Subclasses must implement this method
        """

    def remove(self, session_id):
        """
        Remove the specified session from the session manager.
        """
        self.acquire_lock(session_id)
        try:
            self._remove(session_id)
        finally:
            self.release_lock(session_id)

    def _remove(self, session_id):
        """
        Remove the specified session from the underlying storage.
        Subclasses must implement this method
        """
        raise NotImplementedError

    def _get_session_data(self, session_id):
        """
        Return a dict of the session data from the underlying storage, or
        ``None`` if the session does not exist.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the persistent store cleanly.
        """
        self.acquire_lock()
        try:
            self._close()
        finally:
            self.release_lock()

    def _close(self):
        """
        Default implementation: do nothing
        """

    def purge(self, olderthan=1800):
        for session_id in self._purge_candidates(olderthan):
            self.remove(session_id)

    def _purge_candidates(self, olderthan=1800):
        """
        Return a list of session ids ready to be purged from the session
        manager.
        """
        raise NotImplementedError

    def wsgi_middleware(self, app, auto_purge_every=0, auto_purge_olderthan=1800):

        def sessionmanager_middleware(environ, start_response):

            if environ['wsgi.run_once'] and auto_purge_every > 0:
                self.purge(auto_purge_olderthan)

            session = self.read_session(environ)
            environ['pesto.session'] = session
            environ['pesto.sessionmanager'] = self

            if self.persist == 'cookie' and session.is_new:
                def my_start_response(status, headers, exc_info=None):
                    cookie_path = environ.get('SCRIPT_NAME')
                    if not cookie_path:
                        cookie_path = '/'
                    return start_response(
                        status,
                        list(headers) + [
                            ("Set-Cookie", str(Cookie(Session.COOKIE_NAME, session.session_id, path=cookie_path)))
                        ],
                        exc_info
                    )
            else:
                my_start_response = start_response

            return ClosingIterator(app(environ, my_start_response), session.save)

        return sessionmanager_middleware

class ThreadsafeSessionManagerBase(SessionManagerBase):
    """
    Base class for sessioning to run in a threaded environment.

    DOES NOT GUARANTEE PROCESS-LEVEL SAFETY!
    """

    def __init__(self, persist='cookie'):
        super(ThreadsafeSessionManagerBase, self).__init__(persist)
        self._access_times = {}
        self._lock = threading.RLock()

    def _purge_candidates(self, olderthan=1800):
        """
        Purge all sessions older than ``olderthan`` seconds.
        """
        expiry = time.time() - olderthan
        self.acquire_lock()
        try:
            return [
                id for id, access_time in self._access_times.iteritems() if access_time < expiry
            ]
        finally:
            self.release_lock()

    def acquire_lock(self, session_id=None):
        self._lock.acquire()

    def release_lock(self, session_id=None):
        self._lock.release()

    def update_access_time(self, session_id):
        self.acquire_lock()
        try:
            self._access_times[session_id] = time.time()
        finally:
            self.release_lock()

    def _remove(self, session_id):
        """
        Subclasses should call this implementation to ensure the access_times
        dictionary is kept up to date.
        """
        try:
            del self._access_times[session_id]
        except KeyError:
            logging.warn("tried to remove non-existant session id %r", session_id)

    def __contains__(self, session_id):
        return session_id in self._access_times

def start_thread_purger(sessionmanager, howoften=60, olderthan=1800, lock=threading.Lock()):
    """
    Start a thread to purge sessions older than ``olderthan`` seconds every
    ``howoften`` seconds.
    """

    def _purge():
        while True:
            time.sleep(howoften)
            sessionmanager.purge(olderthan)

    lock.acquire()
    try:
        if hasattr(sessionmanager, '_purge_thread'):
            # Don't start the thread twice
            return
        sessionmanager._purge_thread = threading.Thread(target=_purge)
        sessionmanager._purge_thread.setDaemon(True)
        sessionmanager._purge_thread.start()

    finally:
        lock.release()

def session_middleware(
    session_manager,
    auto_purge_every=60,
    auto_purge_olderthan=1800
):
    """
    WSGI middleware application for sessioning.

    Synopsis::

        >>> from pesto.session.dbmsessionmanager import DBMSessionManager
        >>> def my_wsgi_app(environ, start_response):
        ...     session = environ['pesto.session']
        ... 
        >>> app = session_middleware(DBMSessionManager())(my_wsgi_app)
        >>> 

    session_manager
        An implementation of ``pesto.session.base.SessionManagerBase``

    auto_purge_every
        If non-zero, a separate thread will be launched which will purge
        expired sessions every ``auto_purge_every`` seconds. In a CGI
        environment (or equivalent, detected via, ``environ['wsgi.run_once']``)
        the session manager will be purged after every request.

    auto_purge_olderthan
        Auto purge sessions older than ``auto_purge_olderthan`` seconds.

    """

    def middleware(fn):

        if auto_purge_every > 0:
            start_thread_purger(
                session_manager,
                howoften = auto_purge_every,
                olderthan = auto_purge_olderthan
            )

        return session_manager.wsgi_middleware(fn, auto_purge_every=auto_purge_every, auto_purge_olderthan=auto_purge_olderthan)

    return middleware

