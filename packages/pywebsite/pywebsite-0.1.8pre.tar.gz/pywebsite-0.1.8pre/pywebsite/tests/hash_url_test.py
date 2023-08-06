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
        salt = "thesepretz"
        keys = None
        hash = hash_url.hash_url(values, salt, keys = keys)
        self.assertEqual(hash, 'cf9501e1eb0c3f22801199bc3771e04e')
        # different salt, different hash.
        hash2 = hash_url.hash_url(values, 'differentsalt', keys = None)
        self.assertEqual(hash2, '6ba409389d8513541d6da00ce672b2d1')

        # see that the hash is ok.
        self.assertTrue( hash_url.url_ok(values, salt, hash, keys=keys) )

        keys = ['k1', 'k2']
        hash = hash_url.hash_url(values, salt, keys = keys)
        self.assertTrue( hash_url.url_ok(values, salt, hash, keys=keys) )

        # if we only use the first 6 characters see if that is ok too.
        self.assertTrue( hash_url.url_ok(values, salt, hash[:6], 
                                         keys=keys, length_used = 6) )





if __name__ == '__main__':
    unittest.main()

