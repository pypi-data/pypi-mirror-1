#! /usr/bin/env python

"""Installation script for softwarefabrica.django.wiki
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

from softwarefabrica.django.wiki.version import VERSION, get_version_setuptools
from softwarefabrica.django.utils.finddata import find_package_data

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
    name = "softwarefabrica.django.wiki",
    version = version,
    author = 'Marco Pantaleoni',
    author_email = 'm.pantaleoni@softwarefabrica.org',
    url = 'http://pypi.python.org/pypi/softwarefabrica.django.wiki/',
    download_url = 'http://pypi.python.org/packages/source/s/softwarefabrica.django.wiki/softwarefabrica.django.wiki-%s.tar.gz' % pypi_version,
    #download = 'http://www.softwarefabrica.org/downloads/softwarefabrica.django.wiki.tar.gz',
    license = 'GNU GPL v2',
    description = 'A simple but very flexible django wiki application',
    long_description = long_description,
    keywords = 'django wiki softwarefabrica',
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
    zip_safe = False,
    setup_requires=['setuptools',
                    'django>=1.0',
                    'sflib>=1.0dev-BZR-r45',
                    ],
    install_requires=['setuptools',
                      'django>=1.0',
                      'BeautifulSoup>=3.0.4',
                      'markdown>=1.7',
                      #'python-markdown-tables>=0.1',
                      #'markdown2>=1.0.1.11',
                      #'kiwi>=0.8.3',
                      #'asciidoc>=8.3.0',
                      'sflib>=1.0dev-BZR-r45',
                      'softwarefabrica.django.utils',
                      'softwarefabrica.django.forms',
                      'softwarefabrica.django.crud',
                      # -*- Extra requirements: -*-
                      ],
    extras_require = {
        'PDF':  ["ReportLab>=1.2", "RXP"],
        'reST': ["docutils>=0.3"],
        'markdown': ["markdown>=1.7"],
        #'markdown': ["markdown>=1.7", "python-markdown-tables>=0.1"],
        'markdown2': ["markdown2>=1.0.1.11"],
        'kiwi': ["kiwi>=0.8.3"],
        'asciidoc': ["asciidoc>=8.3.0"],
        'sync': ["sqlalchemy>=0.3.10"],
    },
    test_suite='nose.collector',
    tests_require=['Nose'],
    entry_points = {
        'console_scripts': [
            'sf-import-twiki = softwarefabrica.django.wiki.importer.twiki:main',
            'sf-wiki-sync = softwarefabrica.django.wiki.sync.sync:main [sync]',
        ],
    },
)
