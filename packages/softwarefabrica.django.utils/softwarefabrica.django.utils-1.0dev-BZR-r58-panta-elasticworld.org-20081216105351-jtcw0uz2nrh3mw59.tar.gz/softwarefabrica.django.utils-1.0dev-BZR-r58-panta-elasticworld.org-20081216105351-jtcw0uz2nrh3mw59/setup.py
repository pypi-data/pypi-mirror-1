#! /usr/bin/env python

"""Installation script for softwarefabrica.django.utils
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

from softwarefabrica.django.utils.version import VERSION, get_version_setuptools
#VERSION = "0.9"

# Dynamically calculate the version based on VERSION.
version = get_version_setuptools()

pypi_version = version.replace('_', '-')
pypi_version = version.replace('@', '-')

long_description = (
    read('README.txt') +
    '\n\n' +
    'CHANGES\n' +
    '-------\n\n' +
    read('ChangeLog'))

setup(
    name = "softwarefabrica.django.utils",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://cheeseshop.python.org/pypi/softwarefabrica.django.utils/',
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
    zip_safe = False,                   # we include templates and tests
    setup_requires=['setuptools',
                    'sflib',
                    ],
    install_requires=['setuptools',
                      'django>=1.0',
                      'sflib',
                      # -*- Extra requirements: -*-
                      ],
    test_suite='nose.collector',
    tests_require=['Nose'],
)
