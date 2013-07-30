# -*- coding: utf-8 -*-
import MySQLdb
from MySQLdb.cursors import DictCursor, SSCursor, SSDictCursor
from MySQLdb.cursors import CursorUseResultMixIn


# http://dev.mysql.com/doc/refman/5.5/en/error-messages-client.html
CR_SERVER_GONE_ERROR = 2006


class PendingTransactionError(MySQLdb.DatabaseError):
    pass


class CursorHelper(object):


    _verbs = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

    def __init__(self, cursor):
        self.cursor = cursor
        self.sql_verb = None

    def guess_sql_verb(self, sql, args):
        if args:
            statement = sql % args
        else:
            statement = sql

        verb = statement.strip().split()[0].upper()
        for v in self._verbs:
            if v == verb:
                return v

        return 'SELECT'

    def execute(self, sql, args):
        self.cursor.execute(sql, args)
        self.sql_verb = self.guess_sql_verb(sql, args)

    def result(self):
        if self.sql_verb == 'INSERT':
            r = self.cursor.lastrowid
        elif self.sql_verb == 'UPDATE':
            r = self.cursor.rowcount
        elif self.sql_verb == 'DELETE':
            r = self.cursor.rowcount
        elif self.sql_verb == 'SELECT':
            # if result set is stored on the server side,
            # just return the cursor
            if isinstance(self.cursor, CursorUseResultMixIn):
                r = self.cursor
            else:
                r = self.cursor.fetchall()
        else:
            r = None

        self.sql_verb = None
        return r


class Database(object):
    def __init__(self, **conn_config):
        self.connection_config = {}
        self.connection_config.update(conn_config)
        self.connection = None
        self._in_transaction = False
        self._connect()

    def __enter__(self):
        return self

    def __exit__(self):
        if self._in_transaction:
            self.rollback()
        self.close()

    def _connect(self):
        if self.connection is None:
            self.connection = MySQLdb.connect(**self.connection_config)
            self.connection.autocommit = True

    def close(self):
        if self.connection:
            self.connection.close()
        self.connection = None
        self._in_transaction = False

    def _do_query(self, sql, args, cursor_class):
        ch = CursorHelper(self.connection.cursor(cursor_class))
        ch.execute(sql, args)
        return ch.result()

    def query(self, sql, args=None, cursor_class=DictCursor):
        '''
        A convenient API for common query statement.

        sql -- string, sql to execute on server
        args -- optional sequence or mapping, parameters to use with sql.

        Features:

        - Using DictCursor as default cursor
        - Automaticly reconnect while connection lost(timeout).
        - Return results according to SQL statement verb.

        If you need more detailed control, using cursor directly.
        '''
        try:
            return self._do_query(sql, args, cursor_class)
        except MySQLdb.OperationalError, e:
            # (2006, 'MySQL server has gone away')
            # May lost connection accidentally, try reconnect
            # http://dev.mysql.com/doc/refman/5.5/en/gone-away.html
            if e[0] == CR_SERVER_GONE_ERROR:
                self.close()
                self._connect()
                return self._do_query(sql, args, cursor_class)
            raise

    # transaction 
    def begin(self):
        if self._in_transaction:
            raise PendingTransactionError(
                    'There is pending transaction, '
                    'should be committed or rollbacked')

        self.query('begin')
        self._in_transaction = True

    def commit(self):
        self.query('commit')
        self._in_transaction = False

    def rollback(self):
        self.query('rollback')
        self._in_transaction = False

    # cursor
    @property
    def cursor(self):
        return self.connection.cursor()

    @property
    def dict_cursor(self):
        return self.connection.cursor(DictCursor)

    @property
    def ss_cursor(self):
        return self.connection.cursor(SSCursor)

    @property
    def ss_dict_cursor(self):
        return self.connection.cursor(SSDictCursor)

