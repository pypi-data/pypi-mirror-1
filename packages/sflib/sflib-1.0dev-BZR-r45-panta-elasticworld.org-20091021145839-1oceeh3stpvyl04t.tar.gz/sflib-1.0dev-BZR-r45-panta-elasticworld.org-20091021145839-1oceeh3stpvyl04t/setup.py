#! /usr/bin/env python

"""Installation script for sflib.
Run it with
 './setup.py install', or
 './setup.py --help' for more options
"""

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from sflib.version import VERSION, get_version_setuptools
#VERSION = "0.9"

# Dynamically calculate the version based on VERSION.
version = get_version_setuptools()
pypi_version = version.replace('_', '-')
pypi_version = version.replace('@', '-')

long_description = (open('README.txt').read() + '\n\n' +
                    'CHANGES\n' +
                    '-------\n\n' +
                    open('ChangeLog').read())

# HACK: for some reason 'None' ends in sys.path with python 2.6.1
# so this is required
import sys
while None in sys.path:
    sys.path.remove(None)

setup(
    name = "sflib",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://cheeseshop.python.org/pypi/sflib/',
    download_url = 'http://pypi.python.org/packages/source/s/sflib/sflib-%s.tar.gz' % pypi_version,
    #download = 'http://www.softwarefabrica.org/downloads/sflib.tar.gz',
    license = 'GNU GPL v2',
    description = 'Foundation library for SoftwareFabrica projects',
    long_description = long_description,
    keywords = 'utilities basic foundation',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(exclude=['ez_setup']),
    include_package_data = True,
    exclude_package_data = {
        '': ['.bzr'],
    },
    zip_safe = True,
    install_requires=['setuptools',
                      # -*- Extra requirements: -*-
                      ],
    test_suite='nose.collector',
    tests_require=['Nose'],
)
