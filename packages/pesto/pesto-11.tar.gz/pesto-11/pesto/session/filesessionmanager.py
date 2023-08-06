# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__docformat__ = 'restructuredtext en'
__all__ = ['FileSessionManager',]

"""
Store database sessions in flat files.

Usage::

    >>> from pesto.session import session_middleware
    >>> from pesto.session.filesessionmanager import FileSessionManager
    >>> def my_app(environ, start_response):
    ...     start_response('200 OK', [('Content-Type', 'text/html')])
    ...     yield "<html>Whoa nelly!</html>"
    ...
    >>> manager = FileSessionManager('./sessions', synchronous=True)
    >>> app = session_middleware(manager)(my_app)

"""


import cPickle
import logging
import os
import time
import stat

from pesto.session.base import SessionManagerBase, Session

class FileSessionManager(SessionManagerBase):
    """
    A File-backed session manager.

    Synopsis::

        >>> from pesto.session import session_middleware
        >>> from pesto.session.filesessionmanager import FileSessionManager
        >>> manager = FileSessionManager('/tmp/sessions')
        >>> def app(environ, start_response):
        ...     "WSGI application code here"
        ...
        >>> app = session_middleware(manager)(app)
        >>>

    """

    def __init__(self, directory, persist='cookie'):
        """
        dir
            Path to directory in which session files will be stored.
        """
        super(FileSessionManager, self).__init__(persist)
        self.directory = directory

    def acquire_lock(self, session_id):
        pass

    def release_lock(self, session_id):
        pass

    def get_path(self, session_id):
        """
        Synopsis::

            >>> fsm = FileSessionManager(directory='/tmp')
            >>> session = Session(fsm, 'abcdefgh', True)
            >>> fsm.get_path(session.session_id)
            '/tmp/ab/abcdefgh'
        """

        return os.path.join(self.directory, session_id[:2], session_id)

    def store(self, session):
        path = self.get_path(session.session_id)
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            # Path exists or cannot be created. The latter error will be
            # picked up later :)
            pass

        f = open(path, 'w')
        try:
            cPickle.dump(session.data, f)
        finally:
            f.close()

    def _get_session_data(self, session_id):
        path = self.get_path(session_id)

        try:
            f = open(path, 'r')
        except IOError:
            return None
        try:
            try:
                return cPickle.load(f)
            except (EOFError, IOError):
                logging.exception("Could not read session %r", session_id)
                return None
        finally:
            f.close()

    def update_access_time(self, session_id):
        try:
            os.utime(self.get_path(session_id), None)
        except OSError:
            pass

    def _remove(self, session_id):
        try:
            os.unlink(self.get_path(session_id))
        except OSError:
            logging.exception("Could not remove session file for %r", self.get_path(session_id))

    def _purge_candidates(self, olderthan=1800):
        remove_from = time.time() - olderthan
        for dir, dirs, files in os.walk(self.directory):
            for filename in files:
                if os.stat(os.path.join(dir, filename))[stat.ST_MTIME] < remove_from:
                    yield filename

    def __contains__(self, session_id):
        return os.path.exists(self.get_path(session_id))


