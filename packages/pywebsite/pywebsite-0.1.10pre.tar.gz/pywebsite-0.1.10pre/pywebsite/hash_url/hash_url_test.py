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
from pywebsite import hash_url
import pygame

class TestHashUrl(unittest.TestCase):


    def test_hash(self):

        values = ["image.png", "10"]
        secret_salt = "thesepretz"
        keys = None
        hash = hash_url.hash_url(values, secret_salt, keys = keys)
        self.assertEqual(hash, 'a50db7418ca441c14d71fc3e600bd242c53c2659')
        # different secret_salt, different hash.
        hash2 = hash_url.hash_url(values, 'differentsecret_salt', keys = None)
        self.assertEqual(hash2, 'fe64dfc8c77986937dc52fbe3de0e22258660b14')

        # see that the hash is ok.
        self.assertTrue( hash_url.url_ok(values, secret_salt, hash, keys=keys) )

        keys = ['k1', 'k2']
        hash = hash_url.hash_url(values, secret_salt, keys = keys)
        self.assertTrue( hash_url.url_ok(values, secret_salt, hash, keys=keys) )

        # if we only use the first 6 characters see if that is ok too.
        self.assertTrue( hash_url.url_ok(values, secret_salt, hash[:6], 
                                         keys=keys, length_used = 6) )





if __name__ == '__main__':
    unittest.main()

