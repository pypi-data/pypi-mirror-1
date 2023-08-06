# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__docformat__ = 'restructuredtext en'
__all__ = ['DBMSessionManager',]

"""
A DBM-backed session manager.

Synopsis::

    >>> from pesto.session import session_middleware
    >>> from pesto.session.dbmsessionmanager import DBMSessionManager
    >>> manager = DBMSessionManager('sessions.db', synchronous=True)
    >>> app = session_middleware(manager)(app)

"""


import anydbm
import cPickle
import tempfile

from pesto.session.base import ThreadsafeSessionManagerBase, Session

class DBMSessionManager(ThreadsafeSessionManagerBase):
    """
    A DBM-backed session manager.

    Synopsis::

        >>> from pesto.session import session_middleware
        >>> from pesto.session.dbmsessionmanager import DBMSessionManager
        >>> manager = DBMSessionManager(synchronous=True)
        >>> def app(environ, start_response):
        ...     "WSGI application code here"
        ...
        >>> app = session_middleware(manager)(app)
        >>>
    """

    def __init__(self, filename=None, synchronous=False, persist='cookie'):
        """
        filename
            filename for dbm file. If none, a temporary file is used.

        synchronous
            if ``True``, the ``.sync()`` method will be called on the data
            store after every update.
        """

        super(DBMSessionManager, self).__init__(persist)
        self._synchronous = synchronous

        self.using_temporary_file = (file is None)
        if filename:
            self.filename = filename
        else:
            self.filename = tempfile.mktemp("sessions")

        self.dbm = anydbm.open(self.filename, "c", 0600)

    def _store(self, session):
        self.dbm[session.session_id] = cPickle.dumps(session.data, protocol=self.PICKLE_PROTOCOL)
        if self._synchronous:
            self.dbm.sync()

    def _get_session_data(self, session_id):
        if session_id in self.dbm:
            return cPickle.loads(self.dbm[session_id])
        return None

    def _remove(self, session_id):
        super(DBMSessionManager, self)._remove(session_id)
        try:
            del self.dbm[session_id]
        except KeyError:
            pass
        else:
            if self._synchronous:
                self.dbm.sync()

    def _close(self):
        self.dbm.close()

    def __del__(self):
        self.dbm.close()



