import MySQLdb
import time

class MySQLRecyclingConnection:

    def __init__(self, **kwargs):
        self.connection = MySQLdb.connect(**kwargs)
        self.args = kwargs
        self.start_time = time.time()

    def _check_connection(self):
        if time.time() - self.start_time > 3600:
            self.connection.close()
            self.connection = MySQLdb.connect(**self.args)
            self.start_time = time.time()

    def cursor(self):
        self._check_connection()
        return self.connection.cursor()

    def dbapi():
        return MySQLdb

    def close():
        return self.connection.close()

    def commit(self):
        self._check_connection()
        self.connection.commit()

    def rollback(self):
        self._check_connection()
        self.connection.rollback()


