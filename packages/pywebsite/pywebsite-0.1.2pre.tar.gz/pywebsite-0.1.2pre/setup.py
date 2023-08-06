#!/usr/bin/env python
#
# This is the distutils setup script for pywebsite.
# TODO: Full instructions are in "install.txt" or "install.html"
#
# To configure, compile, install, just run this script.

DESCRIPTION = """pywebsite is for making websites with python.

It is in the pre-alpha stages of life.

"""

EXTRAS = {}

long_description = DESCRIPTION + open('CHANGES.txt','rb').read()

METADATA = {
    'name':             'pywebsite',
    'version':          '0.1.2pre',
    'license':          'LGPL',
    'url':              'http://www.pywebsite.org/',
    'author':           'Rene Dudfield',
    'author_email':     'renesd@gmail.com',
    'description':      'For making websites with python.',
    'long_description': long_description,
    'classifiers':      [
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Internet :: WWW/HTTP :: WSGI',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules ',
    ],
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

