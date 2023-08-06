from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import os

name = 'xanalogica.tumbler'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = name,
    version = '0.1dev',
    author = 'Jeff Rush',
    author_email = 'jeff@taupro.com',
    description = 'Flexible general-purpose coordinate elements with properties of integers and tuples.',
    license = 'GPL 3',
    keywords = ['xanalogica', 'tumblers'],
    url = 'http://www.python.org/pypi/' + name,
    long_description = (
      read('README.txt')
      + '\n' + read('src/xanalogica/tumbler/Tumblers.txt')
      + '\n' + read('TODO.txt')
      + '\n' + read('CHANGES.txt')
      + '\n' + 'Download\n'
      '********\n'
    ),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    # Support unit tests of package
    test_suite = "xanalogica.tumbler.tests",
    tests_require = ['zope.testing'],

    install_requires = ['setuptools'],
    extras_require = {'test': 'zc.buildout'},

    namespace_packages = ['xanalogica', ],
    packages = find_packages('src', exclude=['ez_setup']),
    package_dir = {'': 'src'},
    package_data = {'': ['Tumblers.txt']},
    include_package_data = True,

    zip_safe = True,
    )
