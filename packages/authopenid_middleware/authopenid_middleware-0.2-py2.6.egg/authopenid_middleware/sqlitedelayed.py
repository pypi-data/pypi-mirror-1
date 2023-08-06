from pysqlite2 import dbapi2 as sqlite
import threading

# XXX: I don't have idea if close() should close connections
# in all threads or only in active thread.

class SQLiteDelayed(sqlite.Connection):
    """ This class makes separate SQLite connection
    for each thread because SQLite requires that. """

    def __init__(self, db, **kwargs):
        self.db = db
        self.args = kwargs

        self.connections = {} # connections by thread ID
        self.available = threading.Condition(threading.RLock())

    def _get_connection(self):
        self.available.acquire()
        try:
            tid = threading._get_ident()
            if tid in self.connections:
                return self.connections[tid]
            else:
                connection = sqlite.connect(self.db, **self.args)
                self.connections[tid] = connection
                return connection
        finally:
            self.available.release()

    def cursor(self):
        connection = self._get_connection()
        return connection.cursor()

    def dbapi():
        return sqlite

    def close():
        self.available.acquire()
        try:
            for connection in self.connections:
                connection.close()
        finally:
            self.available.release()

    def commit(self):
        connection = self._get_connection()
        return connection.commit()

    def rollback(self):
        connection = self._get_connection()
        return connection.rollback()
