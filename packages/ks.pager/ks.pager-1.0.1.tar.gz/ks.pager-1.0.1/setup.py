"""Setup for ks.pager package

$Id: setup.py 23736 2007-11-08 18:28:21Z anatoly $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'ks', 'pager', 'README.txt')
    )

setup(
    name = 'ks.pager',
    version = '1.0.1',
    url = 'http://code.keysolutions.ru/ks.pager',
    license = 'ZPL 2.1',
    description = 'Easy get paged listings of objects with ks.formkeeper for Hivurt',
    author = 'Key Solutions Development TEAM',
    author_email = 'ksd-team@keysolutions.ru',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    long_description = long_description,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ks',],
    install_requires = ['setuptools',
                        'zope.interface',
                        'zope.component',
                        'zope.schema',
                        'zope.publisher',
                        ],
    extras_require = dict(
        test = ['zope.testing',
                'ZODB3'],
        ),
    include_package_data = True,
    zip_safe = False,
    )
