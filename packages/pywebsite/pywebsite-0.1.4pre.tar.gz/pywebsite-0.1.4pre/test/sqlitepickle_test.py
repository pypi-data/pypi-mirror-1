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

"""
import time
import unittest
import os
import tempfile
from pywebsite import sqlitepickle

class TestSQLPickle(unittest.TestCase):


    def test_open(self):
        p = sqlitepickle.SQLPickle()
        key, value = 'asdf', 'qwer'
        p.save(key, value)
        value2 = p.get(key)
        self.assertEqual(value, value2)
        p.close()

    def test_rollback(self):
        p = sqlitepickle.SQLPickle()
        key, value = 'asdf', 'qwer'
        p.save(key, value)
        p.rollback()
        self.assertEqual(None, p.get(key))
        self.assertEqual(2, p.get(key, 2))


    def test_afile(self):
        """ try saving to a file.
        """
        f = tempfile.NamedTemporaryFile()
        fname = f.name
        
        p = sqlitepickle.SQLPickle(fname)
        key, value, value2 = 'asdf', 'qwer', 'qwer2'
        p.save(key, value)
        # overwrite the value.
        p.save(key, value2)
        self.assertEqual(value2, p.get(key))
        p.close()
        # cleanup.
        del f
        

    def test_different_data(self):
        """ try saving different types of data
        """
        p = sqlitepickle.SQLPickle()
        key = '2'
        value = {'content': 'w', 'id': '2', 'submit': 'submit', 'title': 'a'}
        p.save(key, value)
        self.assertEqual(value, p.get(key))
        key2 = 2
        p.save(key2, value)
        self.assertEqual(value, p.get(key2))
        #key = (1,2)
        #p.save(key, value)

        p.close()
 




    def xxtest_time(self):
        f = tempfile.NamedTemporaryFile()
        fname = f.name
        
        p = sqlitepickle.SQLPickle(fname)
        key, value, value2 = 'asdf', 'qwer', 'qwer2'
        t1 = time.time()
        num = 10000
        for x in range(num):
            p.save("%s" % x, x)
        t2 = time.time()
        p.save("s", range(num))
        p.close()
        print (t2-t1)
        print (num/ (t2-t1))

        # cleanup.
        del f

if __name__ == '__main__':
    unittest.main()

