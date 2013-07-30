# -*- coding: utf-8 -*-
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


import dbtoy
import datetime


config = {
    'host': 'localhost',
    'user': 'root',
    'db': 'test'
}
db = dbtoy.Database(**config)
now = datetime.datetime.now().replace(microsecond=0)


class Tester(unittest.TestCase):
    def test_a_create_table(self):
        r = db.query('''
CREATE TABLE IF NOT EXISTS `test_case` (
  `id` int(11) unsigned not null auto_increment,
  `name` varchar(32) not null default '',
  `age` tinyint(4) not null default '0',
  `create_at` datetime default null,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`name`)
) ENGINE = INNODB;
''');
        self.assertEqual(r, ())

        r = db.query("SELECT * FROM test_case")
        self.assertEqual(r, ())

    def test_a_show_tables(self):
        r = db.query('SHOW TABLES')
        self.assertEqual(r, ({'Tables_in_test': 'test_case'},))

    def test_b_insert(self):
        r = db.query('''
INSERT INTO test_case (`name`, `age`, `create_at`)
 VALUES (%s, %s, %s)''',
                     ('foo', 18, now))
        self.assertEqual(r, 1)

        r = db.query("SELECT * FROM test_case")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], {'id': 1, 'name': 'foo', 'age': 18, 'create_at': now})

    def test_b_insert_2(self):
        r = db.query('''
INSERT INTO test_case (`name`, `age`, `create_at`)
 VALUES (%s, %s, %s)''',
                     ('bar', 25, now))
        self.assertEqual(r, 2)

        r = db.query("SELECT * FROM test_case")
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1], {'id': 2, 'name': 'bar', 'age': 25, 'create_at': now})

    def test_c_cursor(self):
        from MySQLdb.cursors import Cursor
        r = db.query("SELECT * FROM test_case", cursor_class=Cursor)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], (1, 'foo', 18, now))
        self.assertEqual(r[1], (2, 'bar', 25, now))

    def test_c_cursor_ss(self):
        from MySQLdb.cursors import SSCursor
        r = db.query("SELECT * FROM test_case", cursor_class=SSCursor)
        rs = []
        for i in r:
            rs.append(i)
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[0], (1, 'foo', 18, now))
        self.assertEqual(rs[1], (2, 'bar', 25, now))

    def test_c_cursor_ss_dict(self):
        from MySQLdb.cursors import SSDictCursor
        r = db.query("SELECT * FROM test_case", cursor_class=SSDictCursor)
        rs = []
        for i in r:
            rs.append(i)
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[0], {'id': 1, 'name': 'foo', 'age': 18, 'create_at': now})
        self.assertEqual(rs[1], {'id': 2, 'name': 'bar', 'age': 25, 'create_at': now})

    def test_c_kwargs(self):
        r = db.query("SELECT * FROM test_case WHERE id = %(id)s",
                     {'id': 1})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], {'id': 1, 'name': 'foo', 'age': 18, 'create_at': now})

    def test_d_update(self):
        r = db.query("UPDATE test_case SET age = %(age)s WHERE id = %(id)s",
                     {'age': 28, 'id': 1})
        self.assertEqual(r, 1)

        r = db.query("SELECT * FROM test_case WHERE id = %(id)s",
                     {'id': 1})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], {'id': 1, 'name': 'foo', 'age': 28, 'create_at': now})

    def test_d_update_2(self):
        r = db.query("UPDATE test_case SET age = %(age)s", {'age': 20})
        self.assertEqual(r, 2)

        r = db.query("SELECT age FROM test_case")
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], {'age': 20})
        self.assertEqual(r[1], {'age': 20})

    def test_d_update_3(self):
        r = db.query("UPDATE test_case SET age = %s WHERE id = %s", (0, 10))
        self.assertEqual(r, 0)

    def test_e_delete(self):
        r = db.query("DELETE FROM test_case WHERE name = %s", ('not-found', ))
        self.assertEqual(r, 0)

    def test_e_delete_2(self):
        r = db.query("DELETE FROM test_case WHERE name = %s", ('foo', ))
        self.assertEqual(r, 1)

        r = db.query("SELECT * FROM test_case")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], {'id': 2, 'name': 'bar', 'age': 20, 'create_at': now})

    def test_z_drop_table(self):
        r = db.query('DROP TABLE `test_case`')
        self.assertEqual(r, ())


#if __name__ == '__main__':
#    unittest.main()
