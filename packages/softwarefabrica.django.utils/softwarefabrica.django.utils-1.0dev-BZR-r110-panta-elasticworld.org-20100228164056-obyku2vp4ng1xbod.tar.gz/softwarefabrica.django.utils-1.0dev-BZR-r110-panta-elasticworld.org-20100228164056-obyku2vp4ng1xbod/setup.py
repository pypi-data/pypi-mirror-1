#! /usr/bin/env python

"""Installation script for softwarefabrica.django.utils
Run it with
 './setup.py install', or
 './setup.py --help' for more options
"""

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages
import os, sys

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from softwarefabrica.django.utils.version import VERSION, get_version_setuptools
from softwarefabrica.django.utils.finddata import find_package_data
#VERSION = "0.9"

# Dynamically calculate the version based on VERSION.
version = get_version_setuptools()

pypi_version = version.replace('_', '-')
pypi_version = version.replace('@', '-')

install_requires=['setuptools',
                  'ipaddr>=1.0.1',
                  'django>=1.0',
                  'sflib>=1.0dev-BZR-r45',
                  # -*- Extra requirements: -*-
                  ]

if sys.version_info[:2] < (2, 5):
    install_requires = install_requires + ['uuid',]

long_description = (
    read('docs/overview.txt') +
    '\n\n' +
    'CHANGES\n' +
    '-------\n\n' +
    read('ChangeLog'))

setup(
    name = "softwarefabrica.django.utils",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://pypi.python.org/pypi/softwarefabrica.django.utils/',
    download_url = 'http://pypi.python.org/packages/source/s/softwarefabrica.django.utils/softwarefabrica.django.utils-%s.tar.gz' % pypi_version,
    #download = 'http://www.softwarefabrica.org/downloads/softwarefabrica.django.utils.tar.gz',
    license = 'GNU GPL v2',
    description = 'Utility module for SoftwareFabrica django projects',
    long_description = long_description,
    keywords = 'utility utilities django foundation softwarefabrica',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages=['softwarefabrica', 'softwarefabrica.django'],
    include_package_data = True,
    exclude_package_data = {
        '': ['.bzr'],
    },
    package_data = find_package_data(),
    entry_points = {
        'console_scripts': [
            'sf_display_profile = softwarefabrica.django.utils.display_profile:main',
        ],
    },
    zip_safe = False,                   # we include templates and tests
    setup_requires=['setuptools',
                    'sflib>=1.0dev-BZR-r45',
                    'simplejson>=1.7.1',
                    ],
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=['Nose'],
)
