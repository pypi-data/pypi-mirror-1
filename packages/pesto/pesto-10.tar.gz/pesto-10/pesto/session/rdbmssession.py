# Copyright (c) 2007-2009 Oliver Cope. All rights reserved.
# See LICENCE.TXT for terms of redistribution and use.

__docformat__ = 'restructuredtext en'
__version__ = '2'
__all__ = ['RDBMSSessionManager',]

"""
Session managers for common relational databases.

These are mainly useful for CGI-based environments, where it is not practical
to use the memory or DBM session managers.

Synopsis::

    >>> from pesto.session import session_middleware
    >>> from pesto.session.rdbmsessionmanager import PostgreSQLSessionManager
    >>> from pyPgSQL import PgSQL
    >>>
    >>> # This code will generate a fresh connection everytime the session
    >>> # manager needs to run a query. This is a safe but (very) slow option.
    >>> # Depending on how your application code is written there should be
    >>> # more efficient strategies to employ here!
    >>> manager = PostgreSQLSessionManager(
    ...     connection_factory = partial(PgSQL.connect, database='foo'),
    ...     connection_dispose = lambda conn: conn.close()
    ... )
    >>> app = session_middleware(manager)(app)

"""

import cPickle
import logging
import time

from pesto.session.base import ThreadsafeSessionManagerBase

class RDBMSSessionManager(ThreadsafeSessionManagerBase):

    CREATE_TABLE_SQL = """
        CREATE TABLE pesto_sessions (
            id CHAR(32), 
            data TEXT, 
            last_access_time TIMESTAMP, 
            PRIMARY KEY(id));
    """

    def __init__(self, connection_factory, connection_dispose=None, create_table=True, persist='cookie'):
        """
        connection_factory
            A function that will generate database connections. Must require no
            arguments (use ``functools.partial`` or similar to pre-bind
            connection parameters).

        connection_dispose
            A function that will cleanly dispose of database connections. Must
            require one argument, the connection object.

        create_table
            If ``True``, this class will attempt to create a session table in
            the database. If you are certain the table will already exist,
            switching this to ``False`` will avoid the overhead of this extra
            query.

        Note that this completely ignores the default session access time
        tracking as it's assumed we'll probably be running in a non-persistent
        environment.
        """
        super(RDBMSSessionManager, self).__init__(persist)

        if connection_dispose is None:
            connection_dispose = lambda conn: None

        self.connection_factory = connection_factory
        self.connection_dispose = connection_dispose

        if create_table:
            self._create_session_table()

    def _create_session_table(self, _conn=None):
        if _conn is None:
            conn = self.connection_factory()
        else:
            conn = _conn
        try:
            cursor = conn.cursor()
            try:
                try:
                    cursor.execute(self.CREATE_TABLE_SQL)
                except:
                    # Absorb this error, it almost certainly means the table
                    # already exists
                    pass
                conn.commit()
            finally:
                cursor.close()
        finally:
            if _conn is None:
                self.connection_dispose(conn)

    def __contains__(self, session_id):
        """
        True if the given id exists
        """
        conn = self.connection_factory()
        try:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pesto_sessions WHERE id = %s", (session_id,))
                count = cursor.fetchone()[0]
                return count > 0
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

    def _to_binary(self, bytestr):
        """
        Return the database's binary wrapper for a raw byte-string
        """
        raise NotImplementedError

    def _from_binary(self, binary):
        """
        Return a byte-string from the database's binary wrapper
        """
        raise NotImplementedError

    def _store(self, session):
        """
        Save the session data back to the persistent store
        """
        datapickle = self._to_binary(cPickle.dumps(session.data))

        conn = self.connection_factory()
        try:
            cursor = conn.cursor()
            try:
                for attempt in xrange(3):
                    cursor.execute("SELECT COUNT(*) FROM pesto_sessions WHERE id = %s", (session.session_id,))
                    if cursor.fetchone()[0] == 0:
                        try:
                            cursor.execute(
                                "INSERT INTO pesto_sessions (id, data, last_access_time) VALUES (%s, %s, now())", 
                                (session.session_id, datapickle)
                            )
                            break
                        except:
                            # It's possible for the INSERT to fail due to a race condition here.
                            if attempt == 2:
                                logging.exception("%s: can't store the session for id", session.session_id)
                                raise
                            time.sleep(1)
                            continue

                    else:
                        cursor.execute(
                            "UPDATE pesto_sessions SET data = %s, last_access_time = now() WHERE id = %s", 
                            (datapickle, session.session_id)
                        )
                        break

                conn.commit()
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

    def _remove(self, session_id):
        """
        Removes the specified session from the session manager.
        """
        conn = self.connection_factory()
        try:
            try:
                cursor =  conn.cursor()
                cursor.execute("DELETE FROM pesto_sessions WHERE id = %s", (session_id,))
                conn.commit()
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

    def purge(self, olderthan=1800):
        """
        Purges all sessions older than olderthan seconds.
        """
        raise NotImplementedError

    def _get_session_data(self, session_id):
        row = None
        conn = self.connection_factory()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE pesto_sessions SET last_access_time = now() WHERE id = %s", (session_id, ))
                cursor.execute("SELECT data FROM pesto_sessions WHERE id = %s", (session_id, ))
                row = cursor.fetchone()
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

        if row is None:
            return None
        try:
            return cPickle.loads(self._from_binary(row[0]))
        except:
            # Bad pickles can raise all sorts of exceptions -- in
            # these cases, reset the session and just get on with it...
            pass
        return None

class PostgreSQLSessionManager(RDBMSSessionManager):
    """
    Specialization of RDBMSSessionManager for PostgreSQL.
    """
    CREATE_TABLE_SQL = """
        CREATE TABLE pesto_sessions (
            id CHAR(32), 
            data BYTEA, 
            last_access_time TIMESTAMP, 
            PRIMARY KEY(id));
    """

    def _to_binary(self, bytestr):
        import psycopg2
        return psycopg2.Binary(bytestr)

    def _from_binary(self, binary):
        return str(binary)

    def purge(self, olderthan=1800):
        """
        Purges all sessions older than olderthan seconds.
        """
        conn = self.connection_factory()
        try:
            try:
                cursor =  conn.cursor()
                cursor.execute("""
                    DELETE FROM pesto_sessions 
                    WHERE last_access_time < (now() - INTERVAL '%d SECOND')
                """ % olderthan)
                conn.commit()
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

 

class MySQLSessionManager(RDBMSSessionManager):
    """
    Specialization of RDBMSSessionManager for MySQL.
    """

    def purge(self, olderthan=1800):
        """
        Purges all sessions older than olderthan seconds.
        """
        conn = self.connection_factory()
        try:
            try:
                cursor =  conn.cursor()
                cursor.execute("""
                    DELETE FROM pesto_sessions 
                    WHERE last_access_time < (now() - INTERVAL '%d' SECOND)
                """ % olderthan)
                conn.commit()
            finally:
                cursor.close()
        finally:
            self.connection_dispose(conn)

    def _to_binary(self, binary):
        return str(binary)
