dbtoy
=====

Convenient wrapper and utilities for database operations

Features
--------

Using `Database.query(sql, args)` API for almost every SQL execute.

It havs belowing useful improvements:

- Using DictCursor as default cursor
- Automaticly reconnect while connection lost (2006, 'MySQL server has gone away').
- Smart results return according to SQL statement verb.

Others:

- Transaction API for avoiding mis-commit pending transaction.
- Full test case covered.

Install
-------

    make install

Usage
-----

In most case, using `Database.query(sql, args)` is enough.

If you need more detailed control, using `connection` or `cursor` directly.

API
~~~

- **query** (sql, args=None, cursor_class=DictCursor)

  Execute a SQL statement.

  - query -- string, query to execute on server

  - args -- optional sequence or mapping, parameters to use with query.

  - cursor_class -- change cursor here. for example using SSCursor for result set store in sever side.

  Note: If args is a sequence, then %s must be used as the parameter placeholder in the sql. If a mapping is used, %(key)s must be used as the placeholder.


  Returns: -- Smart results return according to SQL statement verb.

  - INSERT

    long integer `cursor.lastrowid`

  - UPDATE/DELETE

    long integer `cursor.rowcount`

  - SELECT

    if result set store in sever-side, return `cursor`.

    otherwise, return the result set(`cursor.fetchall()`).

  - Others

    return `cursor.fetchall()`.



Example code
~~~~~~~~~~~~

::

    import dbtoy
    db = dbtoy.Database(**config)
    print db.query('SELECT * FROM user WHERE id = %(id)s', {'id': 163})

