#! /usr/bin/env python

"""Installation script for softwarefabrica.django.appserver
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

from softwarefabrica.django.appserver.version import VERSION, get_version_setuptools
from softwarefabrica.django.appserver.finddata import find_package_data
#VERSION = "0.9"

# Dynamically calculate the version based on VERSION.
version = get_version_setuptools()

pypi_version = version.replace('_', '-')
pypi_version = version.replace('@', '-')

long_description = (
    read('docs/overview.txt') +
    '\n\n' +
    'CHANGES\n' +
    '-------\n\n' +
    read('ChangeLog'))

setup(
    name = "softwarefabrica.django.appserver",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://cheeseshop.python.org/pypi/softwarefabrica.django.appserver/',
    download_url = 'http://pypi.python.org/packages/source/s/softwarefabrica.django.appserver/softwarefabrica.django.appserver-%s.tar.gz' % pypi_version,
    #download = 'http://www.softwarefabrica.org/downloads/softwarefabrica.django.appserver.tar.gz',
    license = 'GNU GPL v2',
    description = 'Django HTTP(S) application server',
    long_description = long_description,
    keywords = 'django application server http https web',
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
    #package_data = {
    #    'softwarefabrica.django.appserver': ['*.conf'],
    #},
    entry_points = {
        'console_scripts': [
            'djangoserve = softwarefabrica.django.appserver.djangoserve:main',
        ],
    },
    zip_safe = True,                   # we don't include templates or other files
    setup_requires=['setuptools',
                    'sflib>=1.0dev-BZR-r45',
                    ],
    install_requires=['setuptools',
                      'django>=1.0',
                      'sflib>=1.0dev-BZR-r45',
                      # -*- Extra requirements: -*-
                      ],
    test_suite='nose.collector',
    tests_require=['Nose'],
)
