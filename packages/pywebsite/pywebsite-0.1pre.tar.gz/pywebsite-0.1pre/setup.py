#!/usr/bin/env python
#
# This is the distutils setup script for pywebsite.
# TODO: Full instructions are in "install.txt" or "install.html"
#
# To configure, compile, install, just run this script.

DESCRIPTION = """pywebsite is for making websites with pythong
"""
EXTRAS = {}

METADATA = {
    'name':             'pywebsite',
    'version':          '0.1pre',
    'license':          'LGPL',
    'url':              'http://www.pywebsite.org/',
    'author':           'Rene Dudfield',
    'author_email':     'renesd@gmail.com',
    'description':      'For making websites with python.',
}

import sys

if "bdist_msi" in sys.argv:
    # hack the version name to a format msi doesn't have trouble with
    METADATA["version"] = METADATA["version"].replace("pre", "a0")
    METADATA["version"] = METADATA["version"].replace("rc", "b0")
    METADATA["version"] = METADATA["version"].replace("release", "")


cmdclass = {}
PACKAGEDATA = {
    'cmdclass':    cmdclass,

    'package_dir': {'pywebsite': 'lib',
                    'pywebsite.tests': 'test',
                    'pywebsite.docs': 'docs',
                    'pywebsite.examples': 'examples'},
    'packages': ['pywebsite'],
}






from distutils.core import setup, Command

# allow optionally using setuptools for bdist_egg.
if "-setuptools" in sys.argv:
    from setuptools import setup, Command
    sys.argv.remove ("-setuptools")

    EXTRAS.update({'include_package_data': True,
                   'install_requires': [],
                   'zip_safe': False,
                   }
    )


# test command.  For doing 'python setup.py test'
class TestCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        runs the tests with default options.
        '''
        import subprocess
        return subprocess.call([sys.executable, "run_tests.py"])

cmdclass['test'] = TestCommand



PACKAGEDATA.update(METADATA)
PACKAGEDATA.update(EXTRAS)
setup(**PACKAGEDATA)

