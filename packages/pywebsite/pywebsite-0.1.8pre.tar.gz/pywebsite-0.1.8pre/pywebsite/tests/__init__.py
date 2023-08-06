#!/usr/bin/env python
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
import sys, os, re, unittest

test_subdir = ""
test_subdir = os.path.join('pywebsite', 'tests')
test_subdir = os.path.realpath(os.path.split(__file__)[0]) 

verbose = False

def load_suites(test_subdir):
    # Load all the tests
    suite = unittest.TestSuite()
    test_module_re = re.compile('^(.+_test)\.py$')
    for file in os.listdir(test_subdir):
        for module in test_module_re.findall(file):
            if module in ["XXX_test"]:
                continue
            print ('loading ' + module)
            __import__( module )
            test = unittest.defaultTestLoader.loadTestsFromName( module )
            suite.addTest( test )
    return suite


def main():
    sys.path.insert( 0, test_subdir )
    suite = load_suites(test_subdir)

    # Run the tests
    runner = unittest.TextTestRunner()

    if verbose: 
        runner.verbosity = 2
    runner.run( suite )

if __name__ == "__main__":
    main()

