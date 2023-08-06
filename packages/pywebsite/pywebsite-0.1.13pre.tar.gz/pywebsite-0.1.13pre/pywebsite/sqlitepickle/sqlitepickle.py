##    pywebsite - Python Website Library
##    Copyright (C) 2009 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
"""
Using sqlite3 and the pickle module for a simple key value store,
where the keys are text and the values are pickled objects.

Compatible with python2.6 and python3.1 and python2.5 (with pysqlite2).

>>> db = SQLPickle()
>>> db.save('key', 'value')
>>> db.get('key')
'value'


sqlite3:
    http://docs.python.org/3.1/library/sqlite3.html
pickle:
    http://docs.python.org/3.1/library/pickle.html


"""

import sys
try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import UserDict
    UserDict = UserDict.UserDict
except ImportError:
    import collections
    UserDict = collections.UserDict

serialiser = pickle
sqlite3.register_converter("pickle", serialiser.loads)


class SQLPickle(object):

    def __init__(self, database = ':memory:', table_name = 'key_values'):
        self.open(database, table_name)

    def _connect(self, **kwargs):
        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        kwargs['detect_types'] = detect_types
        self._conn = sqlite3.connect(**kwargs)

    def open(self, database = ':memory:', table_name = 'key_values'):
        """open() opens the database in memory.
           open(filename) opens the database at the given filename.
           open(':memory:') opens an in memory database.
           open(table_name = 'key_values') opens the database and 
               uses the given table name.
        """

        self._table_name = table_name
        self._connect(database=database)
        self._cursor = self._conn.cursor()
        # fields by name, comment out for normal rows.
        self._cursor.row_factory = sqlite3.Row

        q = """create table %s (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  key text,
                  value pickle,
                  UNIQUE (key)
               );
            """ % self._table_name
        try:
            self._conn.execute(q)
        except sqlite3.OperationalError:
            pass
            # the table most likely already exists.


    def save(self, key, value):
        """ save(key, value) adds the value for the given key.
            Overwrites any existing keys value if there is already one.

            Note, does not commit automatically.
        """
        # use the highest and fastest protocol available.
        data_string = sqlite3.Binary( serialiser.dumps(value, 2) )
        try:
            self._conn.execute("insert into %s values (null, ?, ?)" % self._table_name, 
                               (key, data_string,))
        except sqlite3.IntegrityError:
            # update instead
            self._conn.execute("update %s set value = ? where key = ?" % self._table_name, 
                               (data_string, key))


    def get(self, key, default = None):
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        q = "select * from %s where key = ?" % self._table_name
        arow = self._cursor.execute(q, (key,)).fetchone()
        if arow is None:
            return default
        return arow['value']

    def keys(self):
        """ keys() returns a generator of keys.
        """
        q = "select key from %s" % self._table_name
        rows = self._cursor.execute(q).fetchall()
        return (row['key'] for row in rows)

    def items(self):
        """ items() returns a generator of (key,value) pairs.
        """
        q = "select * from %s" % self._table_name
        rows = self._cursor.execute(q).fetchall()
        return ((row['key'], row['value']) for row in rows)




    def commit(self):
        """commit() commits the changes.
        """
        self._conn.commit()

    def rollback(self):
        """rollback() rolls back the changes.
        """
        self._conn.rollback()

    def close(self):
        """close() closes the database connection.
        """
        self._conn.close()




